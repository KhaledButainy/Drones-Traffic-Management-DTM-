import os
import secrets
from datetime import datetime
from flask import flash, render_template, url_for, flash, redirect, request
from dtm import app, mongo, users, bcrypt
from dtm.forms import RegistraionFrom, LoginForm, UpdateAccountForm
from dtm.models import User
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
    if form.validate_on_submit():
        #dding user to the database  
        expireDate = form.expireDate.data          
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        user = {'username':form.username.data,
                'email':form.email.data,
                'certificateID':form.certificateID.data,
                'expireDate': datetime.today().date().replace(year=expireDate.year, month=expireDate.month, day=expireDate.day),
                'password':hashed_password,
                'address':form.address.data,
                'phoneNumber':form.phoneNumber.data}
        users.insert_one(user)
        flash(f'Account created for {form.username.data}! Now you can log in.', 'success')
        return redirect(url_for('home'))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            login_user(User.get_user(form.email.data))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful! Please, check your email and password.', 'danger')
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phoneNumber = form.phoneNumber.data
        current_user.address = form.address.data
        users.update_one({"email": form.email.data}, {'$set': {
            'username': current_user.username,
            'email':current_user.email,
            'phoneNumber':current_user.phoneNumber,
            'address':current_user.address,
        }})
        flash(f'Your account has been updated.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.phoneNumber.data = current_user.phoneNumber
        form.address.data = current_user.address

    return render_template('account.html', title='Account', form=form)

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
