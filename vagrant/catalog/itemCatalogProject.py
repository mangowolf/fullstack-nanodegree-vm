from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
#from oauth2client.client import flow_from_clientsecrets
#from oauth2client.client import FlowExchangeError
#import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

#CLIENT_ID = json.loads(
#	open('client_secrets.json', 'r').read())['web']['client_id']
#APPLICATION_NAME = "Item Catalog Application"

# Connect to database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

## Temporary Fake Data
category = {'name': 'Basketball', 'id': '1'}

categories = [{'name': 'Basketball', 'id': '1'}, {'name': 'Baseball', 'id': '2'}, {'name': 'Football', 'id': '3'},
			  {'name': 'Soccer', 'id': '3'}, {'name': 'Tennis', 'id': '4'}]

items = [{'name':'Wilson_Basketball', 'description':'Standard issue basketball released by NBA.', 'price': '20.00',
		  'id': '1'}, {'name':'Sleeves', 'description':'Sleeve guards for high performance and support.',
		  'price':'40.00', 'id':'2'}, {'name': 'Nike_Air_Jordans', 'description':'Original Air Jordans.',
		  'price':'500.00', 'id':'3'}]

item = {'name':'Wilson_Basketball', 'description':'Standard issue basketball released by NBA.', 'price': '20.00',
		  'id': '1'}


# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
	#categories = session.query(Category).order_by(asc(Category.name))
	return render_template('publicCategories.html', categories=categories)

# Add a new category
@app.route('/category/new')
def addCategory():
	return render_template('newCategory.html')

# Edit a category
@app.route('/category/<int:category_id>/edit')
def editCategory(category_id):
	return render_template('editCategory.html', category_id=category_id)

# Delete a category
@app.route('/category/<int:category_id>/delete')
def delCategory(category_id):
	return render_template('delCategory.html', category_id=category_id)

# Show all items in category
@app.route('/category/<int:category_id>/')
def showCategoryItems(category_id):
	#try:
		#lang = request.args.get('cat_name', type=str)
	return jsonify(result=item)
		#else:
			#return jsonify(result='no items for this category')
	#except Exception as e:
		#return str(e)
		#return render_template('publicCategories.html', category_id=category_id, items=items)

# Display item details
@app.route('/category/<int:category_id>/<int:item_id>/')
def showItem(category_id, item_id):
	return render_template('itemDetails.html', category_id=category_id, item_id=item_id)

# Edit a category item
@app.route('/category/<int:category_id>/<int:item_id>/edit')
def editCategoryItem(category_id, item_id):
	return render_template('editItem.html', category_id=category_id, item_id=item_id)

# Delete a category item
@app.route('/category/<int:category_id>/<int:item_id>/delete')
def delCategoryItem(category_id, item_id):
	return render_template('delItem.html', category_id=category_id, item_id=item_id)




if __name__ == '__main__':
	#app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=1234)