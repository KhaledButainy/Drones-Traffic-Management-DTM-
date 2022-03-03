import os
import secrets
from PIL import Image
from flask import flash, render_template, url_for, flash, redirect, request
from dtm import app, db, bcrypt
from dtm.forms import RegistraionFrom, LoginForm, UpdateAccountForm
from dtm.models import User, Post
from flask_login import login_user, logout_user, current_user, login_required

posts = [
    {
        'author': 'Khaled',
        'title': 'Request 1',
        'content': "First request",
        'date_posted': 'May 24, 2022'
    }
]

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistraionFrom()
    # users.insert_one({'username':'khaled', 'email':'form.email.data', 'certificateID':'form.certificateID.data', 'password':'hashed_password'})

    if form.validate_on_submit():
        #dding user to the database            
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    certificateID=form.certificateID.data,
                    password=hashed_password,
                    address=form.address.data,
                    phoneNumber=form.phoneNumber.data)
        # user.save()
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {form.username.data}! Now you can log in.', 'success')
        return redirect(url_for('home'))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful! Please, check your email and password.', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_certificate(form_certificateID ,form_certificate):
    _, f_ext = os.path.splitext(form_certificate.filename)
    certificate_fn = form_certificateID + f_ext
    certificate_path = os.path.join(app.root_path, 'static/certificates', certificate_fn)
    
    output_size = (500, 500)
    resized_image = Image.open(form_certificate)
    resized_image.thumbnail(output_size)
    resized_image.save(certificate_path)

    return certificate_fn

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    resized_image = Image.open(form_picture)
    resized_image.thumbnail(output_size)
    resized_image.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if form.certificateFile.data:
            certificate_file = save_certificate(current_user.certificateID ,form.certificateFile.data)
            current_user.certificateFile = certificate_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phoneNumber = form.phoneNumber.data
        current_user.address = form.address.data
        db.session.commit()
        flash(f'Your account has been updated.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phoneNumber.data = current_user.phoneNumber
        form.address.data = current_user.address

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title="About")

@app.route("/map")
@login_required
def map():
    return render_template("map.html", title="Map",)

# @app.route("/createAcct")
# @login_required
# def create():
#     return render_template("map.html", title="Map",)
    
    