from datetime import datetime
from dtm import db, mongo, login_manager
from flask_login import UserMixin
from bson.objectid import ObjectId


users = mongo.db.user

@login_manager.user_loader
def load_user(id):
    '''
    Load user for login manager.
    '''
    u = User.get_user_by_id(id)
    if u is None:
        return None
    return u

class User(UserMixin):
    '''
    User class for login manager.
    '''
    def __init__(self, username, password, email, certificateID, expireDate, address, phoneNumber, id):
        self.username = username
        self.password = password
        self.email = email
        self.certificateID = certificateID
        self.expireDate = expireDate
        self.address = address
        self.phoneNumber = phoneNumber
        self.id = id


    @staticmethod
    def get_user(email):
        user = users.find_one({"email": email})
        if user is None:
            return None
        else:
            return User(user['username'], user['password'], user['email'], user['certificateID'], user['expireDate'], user['address'], user['phoneNumber'], user['_id'])

    @staticmethod
    def get_user_by_id(id):
        user = users.find_one({"_id": ObjectId(id)})
        if user is None:
            return None
        else:
            return User(user['username'], user['password'], user['email'], user['certificateID'], user['expireDate'], user['address'], user['phoneNumber'], user['_id'])
