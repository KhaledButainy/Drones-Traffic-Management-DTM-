from crypt import methods
import os
import secrets
import datetime
from flask import flash, render_template, url_for, flash, redirect, request
from dtm import app, users, drones, bcrypt, MAPBOX_ACCESS_TOKEN, MAPBOX_STYLE
from dtm.forms import DroneFrom, RegistraionFrom, LoginForm, UpdateAccountForm
from dtm.models import User
from flask_login import login_user, logout_user, current_user, login_required


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistraionFrom()
    if form.validate_on_submit():
        #adding user to the database  
        expireDate = form.expireDate.data          
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        user = {'username':form.username.data,
                'email':form.email.data,
                'certificateID':form.certificateID.data,
                'expireDate': datetime.datetime.today().replace(year=expireDate.year, month=expireDate.month, day=expireDate.day, hour=0, minute=0, second=0, microsecond=0),
                'password':hashed_password,
                'address':form.address.data,
                'phoneNumber':form.phoneNumber.data,
                'adminAuth' : False}
        users.insert_one(user)
        flash(f'Account created for {form.username.data}! wait for Admin authentication before you can log in.', 'success')
        return redirect(url_for('home'))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = users.find_one({"email": form.email.data})
        if user and user['adminAuth'] == False:
            flash(f'Login unsuccessful! Please, wait for Admin Authentication.', 'danger')
        elif user and bcrypt.check_password_hash(user['password'], form.password.data) and user['adminAuth']:
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
    drone = list(drones.find({"operator_id": current_user.id}))
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

    return render_template('account.html', title='Account', form=form, drones=drone)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/map", methods=['GET', 'POST'])
@login_required
def map():
    drone = list(drones.find({"operator_id": current_user.id}))

    if request.method == 'POST':
        if request.form['options']=='source':
            point_option = request.form['options']
        elif request.form['options']=='distination':
            point_option = request.form['options']
        elif request.form['options'] == 'confirm':
            point_option = None
    else:
        point_option = None
        
    return render_template("map.html", title="Map",
    mapbox_access_token=MAPBOX_ACCESS_TOKEN,
    mapbox_style=MAPBOX_STYLE,
    drones=drone,
    point_option=point_option)

@app.route("/drones", methods=['GET', 'POST'])
@login_required
def drones_route():
    form = DroneFrom()
    if form.validate_on_submit():
        #adding drone to the database  
        droneLicenseExpDate = form.droneLicenseExpDate.data          
        drone = {'type':form.type.data,
                'brand':form.brand.data,
                'weight':form.weight.data,
                'droneLicenseID':form.droneLicenseID.data,
                'droneLicenseExpDate': datetime.datetime.today().replace(year=droneLicenseExpDate.year, month=droneLicenseExpDate.month, day=droneLicenseExpDate.day, hour=0, minute=0, second=0, microsecond=0),
                'operator_id':current_user.id}
        drones.insert_one(drone)
        flash(f'The Drone with the ID ({form.droneLicenseID.data}) is added successfully.', 'success')
        return redirect(url_for('account'))

    return render_template("drones.html", form=form, title="Drones",)

@app.route("/authAccounts", methods=['GET', 'POST'])
def authAccounts():
    unAuthUsers = list(users.find({"adminAuth": False}))
    AuthUsers = list(users.find({"adminAuth": True}))

    return render_template('authAccounts.html', unAuth=unAuthUsers, Auth=AuthUsers)

@app.route('/accept/<user_email>', methods=['GET', 'POST'])
def accept_user(user_email):
    user = users.find_one({'email': user_email})
    flash(f"{user['username']} was Accepted successfully", "success")
    users.update_one({'email': user_email}, {'$set': {'adminAuth': True}})
    return redirect(url_for('authAccounts'))

@app.route('/unaccept/<user_email>', methods=['GET', 'POST'])
def unaccept_user(user_email):
    user = users.find_one({'email': user_email})
    flash(f"{user['username']} was moved to pending requests successfully", "success")
    users.update_one({'email': user_email}, {'$set': {'adminAuth': False}})
    return redirect(url_for('authAccounts'))

@app.route('/reject/<user_email>', methods=['GET', 'POST'])
def reject_user(user_email):
    user = users.find_one({'email': user_email})
    flash(f"{user['username']} was Rejected successfully", "success")
    drones.delete_many({'operator_id': user["_id"]})
    users.delete_one({'email': user_email})
    return redirect(url_for('authAccounts'))


    
    
