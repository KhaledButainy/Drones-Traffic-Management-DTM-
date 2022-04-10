from dtm import users, drones, login_manager
from flask_login import UserMixin
from bson.objectid import ObjectId


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
    def __init__(self, username, password, email, certificateID, expireDate, address, phoneNumber, adminAuth, id):
        self.username = username
        self.password = password
        self.email = email
        self.certificateID = certificateID
        self.expireDate = expireDate
        self.address = address
        self.phoneNumber = phoneNumber
        self.adminAuth = adminAuth
        self.id = id

    @staticmethod
    def get_user(email):
        user = users.find_one({"email": email})
        if user is None:
            return None
        else:
            return User(user['username'], user['password'], user['email'], user['certificateID'], user['expireDate'], user['address'], user['phoneNumber'], user['adminAuth'], user['_id'])

    @staticmethod
    def get_user_by_id(id):
        user = users.find_one({"_id": ObjectId(id)})
        if user is None:
            return None
        else:
            return User(user['username'], user['password'], user['email'], user['certificateID'], user['expireDate'], user['address'], user['phoneNumber'], user['adminAuth'], user['_id'])

class Drone(UserMixin):
    '''
    Drone class for login manager.
    '''
    def __init__(self, type, brand, weight, droneLicenseID, droneLicenseExpDate, operator_id, id):
        self.type = type
        self.brand = brand
        self.weight = weight
        self.droneLicenseID = droneLicenseID
        self.droneLicenseExpDate = droneLicenseExpDate
        self.operator_id = operator_id
        # self.admin_id = admin_id
        self.id = id

    @staticmethod
    def get_drone(droneLicenseID):
        drone = drones.find_one({"droneLicenseID": droneLicenseID})
        if drone is None:
            return None
        else:
            return Drone(drone['type'], drone['brand'], drone['weight'], drone['droneLicenseID'], drone['droneLicenseExpDate'], drone['operator_id'], drone['_id'])

    @staticmethod
    def get_drone_by_id(id):
        drone = drones.find_one({"_id": ObjectId(id)})
        if drone is None:
            return None
        else:
            return Drone(drone['type'], drone['brand'], drone['weight'], drone['droneLicenseID'], drone['droneLicenseExpDate'], drone['operator_id'], drone['_id'])

