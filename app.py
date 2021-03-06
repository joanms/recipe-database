import os

from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo import ASCENDING
from pymongo import DESCENDING
from pymongo import TEXT
import bcrypt


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['MONGO_DBNAME'] = 'recipedb'
app.config['MONGO_URI'] = os.environ.get("MONGO_URI")

mongo = PyMongo(app)
recipes =  mongo.db.recipes

mongo.db.recipes.create_index([('$**', 'text')])
mongo.db.users.create_index([('$**', 'text')])


@app.route('/')
def index():
    
    """Load the home page with links to recipe categories"""
    
    return render_template('index.html', 
        allergens=mongo.db.allergens.find().sort('allergen_name',1), 
        restrictions=mongo.db.restrictions.find().sort('restriction_name',1))


# The register and login routes are based on this code by Pretty Printed: https://github.com/PrettyPrinted/mongodb-user-login/blob/master/login_example.py

@app.route('/register', methods=['POST', 'GET'])
def register():
    
    """Allow new users to register"""
    
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form['username']})

        if existing_user is None:
            # If there is no existing user with that username, encrypt the new user's password
            pw_hash = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            # Decode the hashed password while keeping it encrypted so it can be stored in the MongoDB database
            db_password = pw_hash.decode("utf-8")
            # Add the username and encrypted password to the database
            users.insert({'username' : request.form['username'], 'password' : db_password})
            # The newly registered user is logged in
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        # The user sees this message if their chosen password is already in the database
        flash('That username is taken. Please try a different one.')

    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    
    """Allow registered user to log in"""
    
    if request.method == 'POST':
        users = mongo.db.users
        login_user = users.find_one({'username' : request.form['username']})
    
        if login_user:
            # If the username is in the database, hash the password entered in the form and compare it with the hashed password in the database for that user
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
                session['username'] = request.form['username']
                return redirect(url_for('index'))
    
        # The user sees this message if the username and/or password are invalid
        flash('Invalid username/password combination.')
        
    return render_template('login.html')


@app.route('/user_recipes')
def user_recipes():

    """A page listing the logged-in user's own recipes"""
    
    user = session['username']
    query = ( { 'username': user } )
    results = mongo.db.recipes.find(query).sort('recipe_title',1)
    return render_template('list_recipes.html', 
    recipes=results, count=results.count())
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))    


@app.route('/add_recipe')
def add_recipe():
    
    """Load a form for logged-in users to add a new recipe to the database"""
    
    # The if-else prevents users from submitting recipes when not logged in
    if session:
        return render_template(
            'add_recipe.html', categories=mongo.db.categories.find(), 
            allergens=mongo.db.allergens.find().sort('allergen_name',1), 
            restrictions=mongo.db.restrictions.find().sort('restriction_name',1))
            
    else:
        return redirect(url_for('login'))    


@app.route('/insert_recipe', methods=['GET', 'POST'])
def insert_recipe():
    
    """Post a new recipe to the database and display it after filling in the form"""
    
    recipes =  mongo.db.recipes
    new_recipe = {
        'recipe_title': request.form.get('recipe_title'),
        'image_path': request.form.get('image_path'),
        'category_name': request.form.get('category_name'),
        'author': request.form.get('author'),
        'origin': request.form.get('origin'),
        'servings': request.form.get('servings'),
        'prep_time': request.form.get('prep_time'),
        'extra_time': request.form.get('extra_time'),
        'cook_time': request.form.get('cook_time'),
        'allergens': request.form.getlist('allergens'),
        'restrictions': request.form.getlist('restrictions'),
        'ingredients': request.form.get('ingredients'),
        'method': request.form.get('method'),
        'username': session['username']
    }
    recipes.insert_one(new_recipe)
    return render_template(
        'show_recipe.html', recipe=new_recipe)
    

@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    
    """Load a form to edit a recipe"""
    
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    all_categories = mongo.db.categories.find()
    allergens=mongo.db.allergens.find().sort('allergen_name',1)
    restrictions=mongo.db.restrictions.find().sort('restriction_name',1)
    return render_template(
        'edit_recipe.html', recipe=the_recipe, categories=all_categories, allergens=allergens, restrictions=restrictions)
        

@app.route('/submit_changes/<recipe_id>', methods=['POST'])
def submit_changes(recipe_id):
    
    """Submit changes after editing"""
    
    mongo.db.recipes.update(
        {'_id': ObjectId(recipe_id)},
        {
            'recipe_title': request.form.get('recipe_title'),
            'image_path': request.form.get('image_path'),
            'category_name': request.form.get('category_name'),
            'author': request.form.get('author'),
            'origin': request.form.get('origin'),
            'servings': request.form.get('servings'),
            'prep_time': request.form.get('prep_time'),
            'extra_time': request.form.get('extra_time'),
            'cook_time': request.form.get('cook_time'),
            'allergens': request.form.getlist('allergens'),
            'restrictions': request.form.getlist('restrictions'),
            'ingredients': request.form.get('ingredients'),
            'method': request.form.get('method'),
            'username': session['username']
        })
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template(
        'show_recipe.html', recipe=the_recipe)
    

@app.route('/search', methods=['GET', 'POST'])
def search():
    
    """Search for a recipe by keywords"""
    
    keywords = request.form.get('search')
    query = ( { '$text': { '$search': keywords } } )
    results = mongo.db.recipes.find(query)
    return render_template('list_recipes.html', 
    recipes=results, count=results.count())
    

@app.route('/allergens', methods=['GET', 'POST'])
def allergens():
    
    """Search for recipes without selected allergens"""

    allergens = request.form.getlist('allergens')
    query = ( { 'allergens': { '$nin': allergens} } )
    results = mongo.db.recipes.find(query)
    return render_template('list_recipes.html', 
    recipes=results, count=results.count())


@app.route('/restrictions', methods=['GET', 'POST'])
def restrictions():
    
    """Search for recipes suitable for restricted diets"""

    restrictions = request.form.getlist('restrictions')
    query = ( { 'restrictions': { '$in': restrictions} } )
    results = mongo.db.recipes.find(query)
    return render_template('list_recipes.html', 
    recipes=results, count=results.count())
    

@app.route('/list_recipes', methods=['GET', 'POST'])
def list_recipes():
    
    """List either all recipes in the database or search results"""

    return render_template('list_recipes.html', 
    recipes=recipes.find().sort('recipe_title',1), count=recipes.count())
    

@app.route('/list_recipes_by_cat/<category_name>', methods=['GET', 'POST'])
def list_recipes_by_cat(category_name):
    
    """List recipes by category"""

    results=recipes.find({'category_name': category_name}).sort('recipe_title',1)
    return render_template('list_recipes.html', 
    recipes=results, count=results.count())


@app.route('/show_recipe/<recipe_id>', methods=['GET', 'POST'])
def show_recipe(recipe_id):
    
    """
    Display a recipe, including ingredients, method and other information 
    such as suitability for restricted diets
    """

    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template(
        'show_recipe.html', recipe=the_recipe)


@app.route('/warning/<recipe_id>', methods=['GET', 'POST'])
def warning(recipe_id):
    
    """Display a warning when a user clicks the Delete button"""

    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    flash('This will permanently delete the recipe. Are you sure?')
    return render_template(
        'show_recipe.html', recipe=the_recipe)


@app.route('/delete_recipe/<recipe_id>', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    
    """Delete a recipe when the user clicks the Confirm button"""

    mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('list_recipes'))

    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=False)