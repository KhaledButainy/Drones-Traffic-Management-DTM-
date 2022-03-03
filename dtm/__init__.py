import collections
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from pymongo import MongoClient


app = Flask(__name__)
app.config['SECRET_KEY'] = 'f9c3f15d8972e75a42f1a691020ecd03'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# cluster = MongoClient(host='localhost', port=27017)
# db = cluster['mydb']
# users = db['user']
# drones = db['drone']

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from dtm import routes