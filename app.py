import os

from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from wtforms import Form, BooleanField, TextField, validators
from pymongo import MongoClient
from pymongo import ASCENDING
from pymongo import DESCENDING
from pymongo import TEXT


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['MONGO_DBNAME'] = 'recipedb'
app.config['MONGO_URI'] = 'mongodb://admin:o1deA$@ds127624.mlab.com:27624/recipedb'

mongo = PyMongo(app)
recipes =  mongo.db.recipes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['user'] = username
        users =  mongo.db.users
        users.insert_one(request.form.to_dict())
        flash('Welcome, {}!'.format(username))
        return redirect(url_for('index', username=username))
    return render_template('login.html') 
    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template('index.html')
    

@app.route('/add_recipe')
def add_recipe():
    return render_template(
        'add_recipe.html', categories=mongo.db.categories.find())

@app.route('/insert_recipe', methods=['GET', 'POST'])
def insert_recipe():
    recipes =  mongo.db.recipes
    recipes.insert_one(request.form.to_dict())
    return render_template('list_recipes.html', 
    recipes=recipes.find().sort('_id',-1)) # The recipe list will load with the new recipe at the top
    
# This is based on code from the Code Institute Data-Centric Development Mini Project
@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    all_categories = mongo.db.categories.find()
    return render_template(
        'edit_recipe.html', recipe=the_recipe, categories=all_categories)
        
@app.route('/submit_changes/<recipe_id>', methods=['POST'])
def submit_changes(recipe_id):
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
            'allergens': request.form.get('allergens'),
            'vegetarian': request.form.get('vegetarian'),
            'vegan': request.form.get('vegan'),
            'gluten_free': request.form.get('gluten_free'),
            'ingredients': request.form.get('ingredients'),
            'method': request.form.get('method'),
        })
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template(
        'show_recipe.html', recipe=the_recipe)
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    mongo.db.recipes.create_index([('recipe_title', 'text'), ('author', 'text'), 
    ('origin', 'text'), ('category_name', 'text'), ('ingredients', 'text'), ('method', 'text')])
    keywords = request.form.get('search')
    query = ( { '$text': { '$search': keywords } } )
    results = mongo.db.recipes.find(query)
    return render_template('list_recipes.html', 
    recipes=results)
    
@app.route('/list_recipes', methods=['GET', 'POST'])
def list_recipes():
    return render_template('list_recipes.html', 
    recipes=recipes.find().sort('recipe_title',1))
    
@app.route('/list_recipes_by_cat/<category_name>', methods=['GET', 'POST'])
def list_recipes_by_cat(category_name):
    results=recipes.find({'category_name': category_name}).sort('recipe_title',1)
    return render_template('list_recipes.html', 
    recipes=results)

@app.route('/show_recipe/<recipe_id>', methods=['GET', 'POST'])
def show_recipe(recipe_id):
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template(
        'show_recipe.html', recipe=the_recipe)

@app.route('/warning/<recipe_id>', methods=['GET', 'POST'])
def warning(recipe_id):
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    flash('This will permanently delete the recipe. Are you sure?')
    return render_template(
        'show_recipe.html', recipe=the_recipe)

@app.route('/delete_recipe/<recipe_id>', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('list_recipes'))

    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)