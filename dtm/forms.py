from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from dtm.models import User
from dtm import users, drones


class RegistraionFrom(FlaskForm):
    username = StringField("Operator name", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    certificateID = StringField("GACA Certificate ID", validators=[DataRequired()])
    expireDate = DateField("GACA Certificate Expiry Date", format='%Y-%m-%d', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10)])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # validating if username or op_name is already in the database
        user = users.find({"username": {"$eq":username.data}})
        for document in user:
            if document:
                raise ValidationError("This username already exists. Please choose a different username")
    
    def validate_certificateID(self, certificateID):
        # validating if certificateID is already in the database
        user = users.find({"certificateID": {"$eq":certificateID.data}})
        for document in user:
            if document:
                raise ValidationError("This certificate ID already exists. Please choose a different certificate ID")

    def validate_email(self, email):
        # validating if email is already in the database
        user = users.find({"email": {"$eq":email.data}})
        for document in user:
            if document:
                raise ValidationError("This email already exists. Please choose a different email")
    
    def validate_phoneNumber(self, phoneNumber):
        # validating if phoneNumber is already in the database
        user = users.find({"phoneNumber": {"$eq":phoneNumber.data}})
        
        for document in user:
            if document:
                raise ValidationError("This phone number already exists. Please choose a different phone number")

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField("Username",
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    certificateFile = FileField("GACA Certificate File", validators=[FileAllowed(['jpg', 'png'])])
    address = StringField('Address', validators=[DataRequired()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10)])
    
    submit = SubmitField('Update')

    def validate_username(self, username):
        # validating if username or op_name is already in the database
        if username.data != current_user.username:
            user = users.find({"username": {"$eq":username.data}})
            for document in user:
                if document:
                    raise ValidationError("This username already exists. Please choose a different username")

    def validate_phoneNumber(self, phoneNumber):
        # validating if phoneNumber is already in the database
        if phoneNumber.data != current_user.phoneNumber:
            user = users.find({"phoneNumber": {"$eq":phoneNumber.data}})
            for document in user:
                if document:
                    raise ValidationError("This phone number already exists. Please choose a different phone number")
    
    def validate_email(self, email):
        # validating if email is already in the database
        if email.data != current_user.email:
            user = users.find({"email": {"$eq":email.data}})
            for document in user:
                if document:
                    raise ValidationError("This email already exists. Please choose a different email")

class DroneFrom(FlaskForm):
    type = StringField("Drone Type", validators=[DataRequired()])
    brand = StringField('Drone Brand', validators=[DataRequired()])
    weight = StringField("Weight", validators=[DataRequired()])
    droneLicenseID = StringField("Drone License ID", validators=[DataRequired()])
    droneLicenseExpDate = DateField("Drone License Expiry Date", format='%Y-%m-%d', validators=[DataRequired()])

    submit = SubmitField('Add Drone')

    def validate_droneLicenseID(self, droneLicenseID):
        # validating if droneLicenseID is already in the database
        drone = drones.find({"droneLicenseID": {"$eq":droneLicenseID.data}})
        
        for document in drone:
            if document:
                raise ValidationError("This drone License ID already exists. Please check!")
