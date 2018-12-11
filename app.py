import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_DBNAME"] = 'recipedb'
app.config["MONGO_URI"] = 'mongodb://admin:o1deA$@ds127624.mlab.com:27624/recipedb'

mongo = PyMongo(app)

@app.route('/')
@app.route('/add_recipe')
def add_recipe():
    return render_template('add_recipe.html')


@app.route('/show_recipe')
def show_recipe():
    return render_template("show_recipe.html", 
    recipes=mongo.db.recipes.find())
    
    
if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)