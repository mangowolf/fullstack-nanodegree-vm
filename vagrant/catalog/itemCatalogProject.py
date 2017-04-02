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

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# Connect to database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
					for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
	#Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	#Obtain authorization code
	code = request.data

## Session Commit Convenience Function
def commitSession(argument):
	session.add(argument)
	session.commit()

# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
	categories = session.query(Category).order_by(asc(Category.name))

	return render_template('publicCategories.html', categories=categories)

# Add a new category
@app.route('/category/new', methods=['GET', 'POST'])
def addCategory():
	if request.method == 'POST':
		newCategory = Category(name=request.form['name'])
		commitSession(newCategory)
		displayCategory = session.query(Category).order_by(Category.id.desc()).first()
		return render_template('newCategory.html', newCategory=displayCategory.name)
	else:
		return render_template('newCategory.html')

# Edit a category
@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
	if request.method == "POST":
		editItem = session.query(Category).filter_by(id=category_id).first()
		editItem.name = request.form['name']
		flash('Category updated to new name, %s' % editItem.name)
		commitSession(editItem)
		return redirect(url_for('showCategories'))
	else:
		return render_template('editCategory.html', category_id=category_id)

# Delete a category
@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def delCategory(category_id):
	catToDel = session.query(Category).filter_by(id=category_id).one()
	if request.method == "POST":
		session.delete(catToDel)
		flash('%s successfully deleted' % catToDel.name)
		session.commit()
		return redirect(url_for('showCategories'))
	else:
		return render_template('delCategory.html', category_id=category_id)

# Show all items in category
@app.route('/category/<int:category_id>/')
def showCategoryItems(category_id):
	items = session.query(Item).filter_by(category_id=category_id).all()
	categories = session.query(Category).order_by(asc(Category.name))
	def data_transmitter():
		catItem = []
		for item in items:
			catItem.append(item)
		return catItem
	data = data_transmitter()
	return render_template('publicCategories.html', categories=categories, item=data)


# Add a new Item
@app.route('/category/<int:category_id>/new', methods=['GET','POST'])
def addItem(category_id):
	if request.method == 'POST':
		newItem = Item(name=request.form['name'], description=request.form['description'],
			price=request.form['price'], category_id=category_id)
		commitSession(newItem)
		displayItem = session.query(Item).order_by(Item.id.desc()).first()
		return render_template('newItem.html', category_id=category_id, newItem=displayItem.name)
	else:
		return render_template('newItem.html', category_id=category_id)


# View Item Details
@app.route('/category/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
	itemDetails = session.query(Item).filter_by(id=item_id).one()
	return render_template('itemDetails.html', category_id=category_id, item_id=item_id, 
		item_details=itemDetails)

# Edit a category item
@app.route('/category/<int:category_id>/<int:item_id>/edit', methods=['GET', 'POST'])
def editCategoryItem(category_id, item_id):
	if request.method == "POST":
		itemToEdit = session.query(Item).filter_by(id=item_id).one()
		itemToEdit.name = request.form['name']
		itemToEdit.price = request.form['price']
		itemToEdit.description = request.form['description']
		commitSession(itemToEdit)
		return redirect(url_for('showCategories'))
	else:
		return render_template('editItem.html', category_id=category_id, item_id=item_id)

# Delete a category item
@app.route('/category/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def delCategoryItem(category_id, item_id):
	if request.method == "POST":
		itemToDel = session.query(Item).filter_by(id=item_id).one()
		session.delete(itemToDel)
		session.commit()
		return redirect(url_for('showCategory'))
	else:
		return render_template('delItem.html', category_id=category_id, item_id=item_id)




if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=1234)