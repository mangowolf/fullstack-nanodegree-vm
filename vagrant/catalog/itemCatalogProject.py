from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
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
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])

	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is avlid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's Client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['credentials'] = credentials
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	# Add provider to login session
	login_session['provider'] = 'google'

	# see if user exists, if it doesn't make a new one
	user_id = getUserID(data["email"])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user-id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += 'img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

## Session Commit Convenience Function
def commitSession(argument):
	session.add(argument)
	session.commit()

# user Helper Functions

def createUser(login_session):
	newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
	commitSession(newUser)
	user = session.query(User).filter_by(email=login_session['email']).one()
	return user.id

def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user

def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        #Reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(
          json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


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