import os

from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo import ASCENDING
from pymongo import DESCENDING
from pymongo import TEXT


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
    
    """Home page with links to recipe categories"""
    
    return render_template('index.html', 
        allergens=mongo.db.allergens.find())


@app.route('/add_recipe')
def add_recipe():
    
    """Form to add a new recipe to the database"""
    
    return render_template(
        'add_recipe.html', categories=mongo.db.categories.find(), 
        allergens=mongo.db.allergens.find())


@app.route('/insert_recipe', methods=['GET', 'POST'])
def insert_recipe():
    
    """Post a new recipe to the database after filling in the form"""
    
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
        'vegetarian': request.form.get('vegetarian'),
        'vegan': request.form.get('vegan'),
        'gluten_free': request.form.get('gluten_free'),
        'ingredients': request.form.get('ingredients'),
        'method': request.form.get('method')
    }
    recipes.insert_one(new_recipe)
    return render_template('list_recipes.html', 
    recipes=recipes.find().sort('_id',-1)) # The recipe list will load with the new recipe at the top
    

@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    
    """Form to edit a recipe"""
    
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    all_categories = mongo.db.categories.find()
    allergens=mongo.db.allergens.find()
    return render_template(
        'edit_recipe.html', recipe=the_recipe, categories=all_categories, allergens=allergens)
        

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
            'vegetarian': request.form.get('vegetarian'),
            'vegan': request.form.get('vegan'),
            'gluten_free': request.form.get('gluten_free'),
            'ingredients': request.form.get('ingredients'),
            'method': request.form.get('method')
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
    

@app.route('/vegetarian', methods=['GET', 'POST'])
def vegetarian():
    
    """Search for vegetarian recipes"""
    
    query = ( { 'vegetarian': 'on' } )
    results = mongo.db.recipes.find(query)
    return render_template('list_recipes.html', 
    recipes=results, count=results.count())
    

@app.route('/vegan', methods=['GET', 'POST'])
def vegan():
    
    """Search for vegan recipes"""
    
    query = ( { 'vegan': 'on' } )
    results = mongo.db.recipes.find(query)
    return render_template('list_recipes.html', 
    recipes=results, count=results.count())


@app.route('/gluten_free', methods=['GET', 'POST'])
def gluten_free():
    
    """Search for gluten-free recipes"""

    query = ( { 'gluten_free': 'on' } )
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
    
    """Display a recipe, including ingredients, method and other information 
    such as suitability for restricted diets
    """

    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template(
        'show_recipe.html', recipe=the_recipe)

@app.route('/warning/<recipe_id>', methods=['GET', 'POST'])
def warning(recipe_id):
    
    """A warning dipslays when a user clicks the Delete button"""

    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    flash('This will permanently delete the recipe. Are you sure?')
    return render_template(
        'show_recipe.html', recipe=the_recipe)


@app.route('/delete_recipe/<recipe_id>', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    
    """The recipe is deleted when the user confirms the deletion"""

    mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('list_recipes'))

    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)