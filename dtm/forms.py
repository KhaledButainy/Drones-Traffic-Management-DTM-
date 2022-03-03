from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from dtm.models import User

class RegistraionFrom(FlaskForm):
    username = StringField("Operator name", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    certificateID = StringField("GACA Certificate ID", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10)])
    confirm_pass = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # validating if username or op_name is already in the database
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username already exists. Please choose a different username")
    
    def validate_certificateID(self, certificateID):
        # validating if certificateID is already in the database
        user = User.query.filter_by(certificateID=certificateID.data).first()
        if user:
            raise ValidationError("This certificateID name already exists.")

    def validate_email(self, email):
        # validating if email is already in the database
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email already exists. Please choose a different email")
    
    def validate_phoneNumber(self, phoneNumber):
        # validating if phoneNumber is already in the database
        user = User.query.filter_by(phoneNumber=phoneNumber.data).first()
        if user:
            raise ValidationError("This phone umber already exists. Please choose a different phone number")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField("Username",
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png'])])
    certificateFile = FileField("GACA Certificate File", validators=[FileAllowed(['jpg', 'png'])])
    address = StringField('Address', validators=[DataRequired()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10)])
    
    submit = SubmitField('Update')

    def validate_username(self, username):
        # validating if username is already in the database
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username already exists. Please choose a different username")
    
    def validate_phoneNumber(self, phoneNumber):
        # validating if phoneNumber is already in the database
        if phoneNumber.data != current_user.phoneNumber:
            user = User.query.filter_by(phoneNumber=phoneNumber.data).first()
            if user:
                raise ValidationError("This phone number already exists. Please choose a different phone number")

    def validate_email(self, email):
        # validating if email is already in the database
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email already exists. Please choose a different email")
