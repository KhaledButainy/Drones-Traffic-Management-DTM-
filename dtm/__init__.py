import collections
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f9c3f15d8972e75a42f1a691020ecd03'
app.config["MONGO_URI"] = "mongodb+srv://khaled:1234@cluster0.bdpuf.mongodb.net/mydb?retryWrites=true&w=majority"

mongo = PyMongo(app)
users = mongo.db.user

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from dtm import routes