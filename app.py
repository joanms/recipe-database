import os

from flask import Flask, render_template, redirect, request, url_for, flash
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

@app.route('/add_recipe')
def add_recipe():
    return render_template(
        'add_recipe.html', categories=mongo.db.categories.find())

@app.route('/insert_recipe', methods=['GET', 'POST'])
def insert_recipe():
    recipes =  mongo.db.recipes
    recipes.insert_one(request.form.to_dict())
    return redirect(url_for('list_recipes'))
    
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
    
@app.route('/list_recipes', methods=['GET', 'POST'])
def list_recipes():
    return render_template("list_recipes.html", 
    recipes=mongo.db.recipes.find())

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST': 
        search = (request.form.getlist('search'))
        results = recipes.find({ "$text": { "$search":  "/.*"+search[0]+".*/i" } })
    return render_template("list_recipes.html", 
    recipes=results)
    
@app.route('/bread', methods=['GET', 'POST'])
def bread():
    results=recipes.find({"category_name": "Bread"})
    return render_template("list_recipes.html", 
    recipes=results)

@app.route('/starters', methods=['GET', 'POST'])
def starters():
    results=recipes.find({"category_name": "Starters"})
    return render_template("list_recipes.html", 
    recipes=results)

@app.route('/mains', methods=['GET', 'POST'])
def mains():
    results=recipes.find({"category_name": "Mains"})
    return render_template("list_recipes.html", 
    recipes=results)

@app.route('/sides', methods=['GET', 'POST'])
def sides():
    results=recipes.find({"category_name": "Sides"})
    return render_template("list_recipes.html", 
    recipes=results)

@app.route('/sauces', methods=['GET', 'POST'])
def sauces():
    results=recipes.find({"category_name": "Sauces"})
    return render_template("list_recipes.html", 
    recipes=results)

@app.route('/desserts', methods=['GET', 'POST'])
def desserts():
    results=recipes.find({"category_name": "Desserts"})
    return render_template("list_recipes.html", 
    recipes=results)

@app.route('/show_recipe/<recipe_id>', methods=['GET', 'POST'])
def show_recipe(recipe_id):
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    return render_template(
        'show_recipe.html', recipe=the_recipe)

@app.route('/warning/<recipe_id>', methods=['GET', 'POST'])
def warning(recipe_id):
    the_recipe = mongo.db.recipes.find_one({'_id': ObjectId(recipe_id)})
    flash("Are you sure you want to permanently delete the recipe?")
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