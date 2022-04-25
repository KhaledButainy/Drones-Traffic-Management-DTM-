from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_pymongo import PyMongo
import json

config_json = json.load(open("./dtm/config/config.json"))

app = Flask(__name__)
app.config['SECRET_KEY'] = config_json["SECRET_KEY"]
app.config["MONGO_URI"] = config_json["ATLAS_MONGO_URI"]
# app.config["MONGO_URI"] = config_json["LOCAL_MONGO_URI"]

mongo = PyMongo(app)
users = mongo.db.user
drones = mongo.db.drone
admins = mongo.db.admin


MAPBOX_ACCESS_TOKEN = config_json["MAPBOX_ACCESS_TOKEN"]
MAPBOX_STYLE = config_json["MAPBOX_STYLE"]
DATABASE_NAME = config_json["DATABASE_NAME"]
STITCH_APP_ID = config_json["STITCH_APP_ID"]
ATLAS_MONGO_URI = config_json["ATLAS_MONGO_URI"]

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

for d in config_json['ADMINS']:
    d['password'] = bcrypt.generate_password_hash(d['password']).decode('utf8')

admins.drop()
admins.insert_many(config_json['ADMINS'])


from dtm import routes