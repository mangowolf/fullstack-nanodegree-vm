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

# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
	#categories = session.query(Category).order_by(asc(Category.name))
	return 'Hello World!'


if __name__ == '__main__':
	#app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=1234)