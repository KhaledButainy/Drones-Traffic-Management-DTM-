
from ast import operator
import datetime
from flask import flash, render_template, url_for, flash, redirect, request
from sqlalchemy import false
from dtm import app, users, admins, drones, bcrypt, config_json, MAPBOX_ACCESS_TOKEN, MAPBOX_STYLE, DATABASE_NAME, STITCH_APP_ID
from dtm.forms import DroneFrom, RegistraionFrom, LoginForm, UpdateAccountForm
from dtm.models import User, Admin
from flask_login import login_user, logout_user, current_user, login_required


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistraionFrom()
    if form.validate_on_submit():
        #adding user to the database 
        admin = admins.find_one({"email": form.email.data})
        if admin:
            flash("This email already exists", "danger")
        else:
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
        admin = admins.find_one({"email": form.email.data})
        if admin and bcrypt.check_password_hash(admin['password'], form.password.data):
            login_user(Admin.get_admin(form.email.data))
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        elif user and user['adminAuth'] == False:
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
    drone = list(drones.find({"operator_email": current_user.email}))
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

@app.route("/schedule_map", methods=['GET', 'POST'])
@login_required
def schedule_map(selected_drone = None):
    drone = list(drones.find({"$and": [{"operator_email": current_user.email}, {"connected": True}]}))
    selected_drone = request.args.get('selected_drone')
        
    return render_template("schedule_map.html", title="Schedule a Flight",
    mapbox_access_token=MAPBOX_ACCESS_TOKEN,
    mapbox_style=MAPBOX_STYLE,
    drones=drone,
    selected_drone = selected_drone)

@app.route("/monitor_map", methods=['GET', 'POST'])
@login_required
def monitor_map(selected_operator = "All"):
    drone = list(drones.find({"operator_email": current_user.email}))
    operator = list(users.find({}))
    selected_operator = request.args.get('selected_operator')
    admin = next((admin for admin in config_json['ADMINS'] if admin["email"] == current_user.email), None)
    is_admin = False
    if admin:
        is_admin = True
        if selected_operator == 'All':
            drone = list(drones.find({}))
        else:
            drone = list(drones.find({"operator_email": selected_operator}))
    
    return render_template("monitor_map.html", title="Monitor",
    mapbox_access_token=MAPBOX_ACCESS_TOKEN,
    mapbox_style=MAPBOX_STYLE,
    database_name=DATABASE_NAME,
    stitch_app_id=STITCH_APP_ID,
    current_user_email = current_user.email,
    drones=drone,
    operators=operator,
    is_admin=is_admin,
    selected_operator = selected_operator)

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
                'operator_email':current_user.email,
                'coordinates': [0, 0],
                'altitude': 0,
                'gps_status': 0,
                'armed': False,
                'flight_mode': "Manual",
                'speed': 0,
                'eta': 0,
                'connected': False}
        drones.insert_one(drone)
        flash(f'The Drone with the ID ({form.droneLicenseID.data}) is added successfully.', 'success')
        return redirect(url_for('account'))

    return render_template("drones.html", form=form, title="Drones",)

@app.route("/authAccounts", methods=['GET', 'POST'])
@login_required
def authAccounts():
    unAuthUsers = list(users.find({"adminAuth": False}))
    AuthUsers = list(users.find({"adminAuth": True}))

    return render_template('authAccounts.html', unAuth=unAuthUsers, Auth=AuthUsers)

@app.route('/accept/<user_email>', methods=['GET', 'POST'])
@login_required
def accept_user(user_email):
    user = users.find_one({'email': user_email})
    flash(f"{user['username']} was Accepted successfully", "success")
    users.update_one({'email': user_email}, {'$set': {'adminAuth': True}})
    return redirect(url_for('authAccounts'))

@app.route('/unaccept/<user_email>', methods=['GET', 'POST'])
@login_required
def unaccept_user(user_email):
    user = users.find_one({'email': user_email})
    flash(f"{user['username']} was moved to pending requests successfully", "success")
    users.update_one({'email': user_email}, {'$set': {'adminAuth': False}})
    return redirect(url_for('authAccounts'))

@app.route('/reject/<user_email>', methods=['GET', 'POST'])
@login_required
def reject_user(user_email):
    user = users.find_one({'email': user_email})
    flash(f"{user['username']} was Rejected successfully", "success")
    drones.delete_many({'operator_id': user["_id"]})
    users.delete_one({'email': user_email})
    return redirect(url_for('authAccounts'))

@app.route("/schedule_map_drone_select", methods=['GET', 'POST'])
@login_required
def schedule_map_drone_select():
    selected_drone_lisenceID = request.form.get('drone_select')
    return redirect(url_for('schedule_map', selected_drone = selected_drone_lisenceID))

@app.route("/monitor_map_drone_select", methods=['GET', 'POST'])
@login_required
def monitor_map_drone_select():
    selected_drone_lisenceID = request.form.get('drone_select')
    return redirect(url_for('monitor_map', selected_drone = selected_drone_lisenceID))

@app.route("/monitor_map_drone_filter", methods=['GET', 'POST'])
@login_required
def monitor_map_drone_filter():
    setected_operator_email = request.form.get('operator_select')
    return redirect(url_for('monitor_map', selected_operator = setected_operator_email))

    
