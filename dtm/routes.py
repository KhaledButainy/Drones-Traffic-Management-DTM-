
import datetime
from flask import flash, render_template, url_for, flash, redirect, request, session
from dtm import app, users, admins, drones, current_flights, bcrypt,config_json, broker_client, MAPBOX_ACCESS_TOKEN, MAPBOX_STYLE, DATABASE_NAME, STITCH_APP_ID
from dtm.forms import DroneFrom, RegistraionFrom, LoginForm, UpdateAccountForm
from dtm.models import User, Admin
from flask_login import login_user, logout_user, current_user, login_required
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from copy import deepcopy
from dtm.PathPlanning.Sampling_based_Planning.rrt_3D import rrt_connect3D
import json



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
    return render_template('home.html', title="Home")

@app.route("/schedule_map", methods=['GET', 'POST'])
@login_required
def schedule_map(selected_drone = None):
    drone = list(drones.find({"$and": [{"operator_email": current_user.email}, {"connected": True}]}))
    selected_drone = request.args.get('selected_drone')
    src_dst = request.form.get('store_coordinates')
    mission_path = {"coordinates": []}
    no_fly_zones = json.load(open("./dtm/config/no_fly_zones.json"))

    if request.method =="GET":
        if "flight_src_dst" in session:
            src_dst = session["flight_src_dst"]
            session.pop('flight_src_dst', None)
        if "mission_path" in session:
            mission_path = session['mission_path']
    
    return render_template("schedule_map.html", title="Schedule a Flight",
    mapbox_access_token=MAPBOX_ACCESS_TOKEN,
    mapbox_style=MAPBOX_STYLE,
    drones=drone,
    mission_path = mission_path,
    selected_drone = selected_drone,
    src_dst = src_dst, no_fly_zones=no_fly_zones)

@app.route("/monitor_map", methods=['GET', 'POST'])
@login_required
def monitor_map():
    drone = list(drones.find({"operator_email": current_user.email}))
    no_fly_zones = json.load(open("./dtm/config/no_fly_zones.json"))


    return render_template("monitor_map.html", title="Monitor",
    mapbox_access_token=MAPBOX_ACCESS_TOKEN,
    mapbox_style=MAPBOX_STYLE,
    database_name=DATABASE_NAME,
    stitch_app_id=STITCH_APP_ID,
    current_user_email = current_user.email,
    drones=drone,
    no_fly_zones=no_fly_zones)

@app.route("/admin_monitor_map", methods=['GET', 'POST'])
@login_required
def admin_monitor_map(selected_operator = "All"):
    drone = list(drones.find({}))
    operator = list(users.find({}))
    selected_operator = request.args.get('selected_operator')
    no_fly_zones = json.load(open("./dtm/config/no_fly_zones.json"))

    
    return render_template("admin_monitor_map.html", title="Monitor",
    mapbox_access_token=MAPBOX_ACCESS_TOKEN,
    mapbox_style=MAPBOX_STYLE,
    database_name=DATABASE_NAME,
    stitch_app_id=STITCH_APP_ID,
    drones=drone,
    operators=operator,
    selected_operator = selected_operator,
    no_fly_zones=no_fly_zones)


@app.route("/schedule_map_form_action", methods=['GET', 'POST'])
@login_required
def schedule_map_form_action():
    if request.method =="POST":
        selected_drone_lisenceID = request.form.get('drone_select')
        if request.form["form_btn"] == "select_drone_btn" and selected_drone_lisenceID != "None":
            flash(f"Drone with LicenseID {selected_drone_lisenceID} is selected", 'success')
            if "flight_src_dst" in session:
                session.pop('flight_src_dst', None)
            if "mission_path" in session:
                session.pop('mission', None)

        if request.form["form_btn"] == "create_mission_btn" and selected_drone_lisenceID != "None":
            src_dst = request.form.get('store_coordinates')
            src_dst = src_dst.split(",")
            src_dst_copy = deepcopy(src_dst)
            src_dst = [[float(src_dst[0]), float(src_dst[1])],[float(src_dst[2]), float(src_dst[3])]]
            src_dst_copy = [[float(src_dst_copy[0]), float(src_dst_copy[1]), 0.001],[float(src_dst_copy[2]), float(src_dst_copy[3]), 0.001]]
            src_dst_json = {"start": src_dst[0], "destination": src_dst[1]}
            session["flight_src_dst"] = src_dst_json
            flash(f"Mission is created to Drone with LicenseID {selected_drone_lisenceID}", 'success')
                    
            #here we should pass the src_dst and obstacles from the database and get the mission path
            env_config = json.load(open("./dtm/config/env2_nocube.json"))
            no_fly_zones = json.load(open("./dtm/config/no_fly_zones.json"))
            for key in no_fly_zones:
                for element in no_fly_zones[key]:
                    element.append(10)

            mission_path = {'coordinates': rrt_connect3D.find_new_path(selected_drone_lisenceID, src_dst_copy[0], src_dst_copy[1], env_config, no_fly_zones, False)}
            flight_paths = list(current_flights.find({'droneLicenseID': {"$ne" : selected_drone_lisenceID}}))
            print(flight_paths)
            mission_path = {'coordinates': rrt_connect3D.check_intersects(mission_path['coordinates'], flight_paths)}
            session["mission_path"] = mission_path

        if request.form["form_btn"] == "send_mission_btn" and selected_drone_lisenceID != "None":
            flash(f"Mission is sent to Drone with LicenseID {selected_drone_lisenceID}", 'success')
            mission_str = request.form.get('created_mission')
            broker_address = config_json["BROKER_ADDRESS"]  # Broker address in config
            port = config_json["BROKER_PORT"]  # Broker port in config
            broker_client.username_pw_set(username=config_json["BROKER_CLIENT_USERNAME"], password=config_json["BROKER_CLIENT_PASSWORD"])
            broker_client.connect(broker_address, port=port) 

            if mission_str:
                broker_client.publish("mission", mission_str)
                flight_path = list(current_flights.find({"droneLicenseID": selected_drone_lisenceID}))
                if flight_path:
                    current_flights.update_one({"droneLicenseID": selected_drone_lisenceID}, {"$set": {"flight_path": session["mission_path"]}})
                else:
                    flight_path = {"droneLicenseID": selected_drone_lisenceID, "flight_path": session["mission_path"]}
                    current_flights.insert_one(flight_path)

            session.pop('mission_path', None)


    return redirect(url_for('schedule_map', selected_drone = selected_drone_lisenceID))


@app.route("/monitor_map_operator_filter", methods=['GET', 'POST'])
@login_required
def monitor_map_operator_filter():
    setected_operator_email = request.form.get('operator_select')
    return redirect(url_for('admin_monitor_map', selected_operator = setected_operator_email))


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
                'connected': False,}
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


def check_ongoing_flights():
    flight_path = list(current_flights.find({}))
    if flight_path:
        for fp in flight_path:
            drone = list(drones.find({"droneLicenseID": fp["droneLicenseID"]}))
            if drone:
                if drone[0]["armed"] == False:
                    current_flights.delete_one({"droneLicenseID": fp["droneLicenseID"]})

def check_users_licences_exp_date():
    users_list = list(users.find({}))
    if users_list:
        for user in users_list:
            drones_list = list(drones.find({'operator_id': user["_id"]}))
            if user["expireDate"] < datetime.datetime.now():
                user["adminAuth"] = False
            if drones_list:
                for drone in drones_list:
                    if drone["droneLicenseExpDate"] < datetime.datetime.now():
                        drones.delete_one({"droneLicenseID": drone["droneLicenseID"]})


sched = BackgroundScheduler()
#check every one hour and remove completed flights
sched.add_job(check_ongoing_flights,'interval',minutes=60)
#check every 24 house on expired licenses
sched.add_job(check_users_licences_exp_date,'interval',hours=24)
sched.start()
atexit.register(lambda: sched.shutdown())
