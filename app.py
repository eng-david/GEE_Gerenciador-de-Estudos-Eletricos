import webview

from functools import wraps
from math import sqrt

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import re
import logging

logging.getLogger("cs50").disabled = False

# Configure application
app = Flask(__name__)
webview.create_window('Gerenciador de Estudos Elétricos', app)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///electric.db")

@app.after_request
def after_request(response):
    #Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # get user input username
        username = request.form.get("username")
        # Ensure username was submitted
        if not username:
            flash("must provide username", 'alert-danger')
            return redirect("/register")

        # get user input password
        password = request.form.get("password")
        # get user input password
        confirmation = request.form.get("confirmation")
        # Ensure password and confirmation was submitted
        if not password or not confirmation:
            flash("must provide password", 'alert-danger')
            return redirect("/register")

        # Ensure password and confirmation are equal
        if not (password == confirmation):
            flash("passwords do not match", 'alert-danger')
            return redirect("/register")

        # Validate password with regex
        # Should have at least one number.
        # Should have at least one uppercase and one lowercase character.
        # Should have at least one special symbol.
        # Should be between 6 to 20 characters long.
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        # compiling regex
        pat = re.compile(reg)
        # searching regex
        mat = re.search(pat, password)
        if not mat:
            flash("invalid password", 'alert-danger')
            return redirect("/register")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        # Ensure username not exists
        if len(rows) != 0:
            flash("username already exists", 'alert-danger')
            return redirect("/register")

        # Save user credentials in database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        # get user id from db
        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]

        # Login user
        session.clear()
        session["user_id"] = user_id
        session["username"] = username

        # Redirect user to home page
        flash("Registered!", 'alert-primary')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            # flash error message
            flash("must provide username", 'alert-danger')
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password", 'alert-danger')
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("invalid username and/or password", 'alert-danger')
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/user")
@login_required
def user():
    # render user profile page
    return render_template("user.html")

@app.route("/deleteaccount", methods=["POST"])
@login_required
def deleteaccount():
    
    # get user input password
    password = request.form.get("password")

    # Ensure password was submitted
    if not password:
        # render user profile page with error
        flash('Invalid password provided', 'alert-danger')
        return redirect("/user")

    # Query database for user data
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

    # Ensure password is correct
    if not check_password_hash(rows[0]["hash"], password):
        flash('Invalid password provided', 'alert-danger')
        return redirect("/user")

    # Remove user, user's projects, customers, profiles from db
    db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
    db.execute("DELETE FROM projects WHERE user_id = ?", session["user_id"])
    db.execute("DELETE FROM customers WHERE user_id = ?", session["user_id"])
    db.execute("DELETE FROM profiles WHERE user_id = ?", session["user_id"])

    # Forget any user_id
    session.clear()

    # redirect to login form
    flash("Account Deleted", 'alert-danger')
    return render_template("login.html")

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # get user input actual password
        actual_password = request.form.get("actualpassword")
        # ensures actual password exists
        if not actual_password:
            flash("must provide actual password", 'alert-danger')
            return redirect("/changepassword")

        # get user input new password
        newpassword = request.form.get("newpassword")
        # ensures new password exists
        if not newpassword:
            flash("must provide new password", 'alert-danger')
            return redirect("/changepassword")

        # get user input confirmation
        confirmation = request.form.get("confirmation")
        # ensures confirmation exists
        if not confirmation:
            flash("must provide confirmation", 'alert-danger')
            return redirect("/changepassword")

        # Ensure password and confirmation are equal
        if not (newpassword == confirmation):
            flash("passwords do not match", 'alert-danger')
            return redirect("/changepassword")

        # Validate password with regex
        # Should have at least one number.
        # Should have at least one uppercase and one lowercase character.
        # Should have at least one special symbol.
        # Should be between 6 to 20 characters long.
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        # compiling regex
        pat = re.compile(reg)
        # searching regex
        mat = re.search(pat, newpassword)
        if not mat:
            flash("invalid password", 'alert-danger')
            return redirect("/changepassword")

        # Query database for username
        user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Validade if actual password input is correct
        if not check_password_hash(user[0]["hash"], actual_password):
            flash("invalid actual password", 'alert-danger')
            return redirect("/changepassword")

        # Save user credentials in database
        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(newpassword), session["user_id"])

        # Redirect user to home page
        flash("Password Changed!", 'alert-primary')
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changepass.html")

@app.route("/")
@login_required
def index():
    
    # get actual user projects list
    projects = db.execute("SELECT projects.id, projects.name, customers.name AS customerName, projects.createddate, projects.modifieddate \
                            FROM projects \
                            LEFT JOIN customers on customers.id = projects.customer_id \
                            WHERE projects.user_id = ? \
                            ORDER BY projects.modifieddate DESC", session["user_id"])

    # Render projects page
    return render_template("index.html", projects=projects)

@app.route("/project", methods=["GET", "POST"])
@login_required
def project():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # if user have click on delete button
        # get id of project to delete
        delete = request.form.get("delete")
        if delete != None:
            db.execute("DELETE FROM projects WHERE id = ? AND user_id = ?", delete, session["user_id"])
            db.execute("DELETE FROM transformers WHERE project_id = ?", delete)
            flash("Project Deleted", 'alert-primary')
            return redirect("/")

        # get project id
        id = request.form.get("id")

        # ensures id belongs to user
        if id:
            # if no one item throws out of range index
            db.execute("SELECT id FROM projects WHERE id = ? AND user_id = ?", id, session["user_id"])[0]

        parameter_list = ["name", "customer_id", "profile_id", "voltage", "demand", "pf", "tri_sc", "bi_sc", "lg_sc_max", "lg_sc_min"]
        
        # get web page input data
        parameter = {}
        for item in parameter_list:
            parameter[item] = request.form.get(item)

        if not parameter["name"]: parameter["name"] = "noname"

        now = datetime.now()

        # if no id is a new project then create a new entry in db
        if not id:
            id = db.execute("INSERT INTO projects (user_id, createddate) VALUES (?, ?)", session["user_id"], now)

        # update project data
        db.execute("UPDATE projects SET modifieddate = ? WHERE id = ? AND user_id = ?", now, id, session["user_id"])
        for item in parameter_list:
            string = "UPDATE projects SET " + item + " = ? WHERE id = ? AND user_id = ?"
            db.execute(string, parameter[item], str(id), str(session["user_id"]))


        # update project's transformers data
        transformersData = db.execute("SELECT id FROM transformers WHERE project_id = ?", id)
        for transformer in transformersData:

            t_id = str(transformer["id"])

            kva = request.form.get("kva_" + t_id)
            impedance = request.form.get("impedance_" + t_id)
            type = request.form.get("type_" + t_id)
            if not type:
                type = 0

            db.execute("UPDATE transformers SET power_kva = ?, impedance = ?, type = ? WHERE id = ?", kva, impedance, type, t_id)


        add_tr = request.form.get("add_tr")
        if (add_tr == "1"):
            db.execute("INSERT INTO transformers (project_id, power_kva, impedance, type) VALUES (?, ?, ?, ?)", id, "0", "0", None)

        delete_tr = request.form.get("delete_tr")
        if delete_tr:
            db.execute("DELETE FROM transformers WHERE id = ? AND project_id = ?", delete_tr, id)
        
        
        # redirect
        page_id = request.form.get("page_id")
        flash(parameter["name"] + " saved", 'alert-primary')
        if page_id == "diagram":
            return redirect("/diagram?id=" + str(id))
        return redirect("/project?id=" + str(id) + "&go=" + page_id)

     # User reached route via GET (as by clicking a link or via redirect)
    else:
        # get user customers list
        customersData = db.execute("SELECT id, name FROM customers WHERE user_id = ?", session["user_id"])

        # get user profiles list
        profilesData = db.execute("SELECT id, name FROM profiles WHERE user_id = ?", session["user_id"])

        # get destination
        go = request.args.get("go")

        # get id if user have click edit on customers page
        id = request.args.get("id")

        # if user have click in edit in customers page
        if id:
            projectData = db.execute("SELECT * FROM projects WHERE id = ? and user_id = ?", id, session["user_id"])[0]
            transformersData = db.execute("SELECT * FROM transformers WHERE project_id = ?", id)
        else:
            projectData = None
            transformersData = None
        
        return render_template("project.html", go=go, customersData=customersData, profilesData=profilesData, projectData=projectData, transformersData=transformersData)

@app.route("/duplicate")
@login_required
def duplicate():
    # get id of project to duplicate
    id = request.args.get("id")

    # get type of item to duplicate
    ob = request.args.get("ob")

    # get actual date
    now = datetime.now()

    if ob == "project":
        # get referenced project data from db
        project = db.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", id, session["user_id"])[0]

        # remove non duplicated keys from dict
        project_id = project["id"]
        del project["id"]
        del project["createddate"]
        del project["modifieddate"]

        # add "copy" to name
        project["name"] += " (copy)"

        # create a new project entry in db
        new_id = db.execute("INSERT INTO projects (user_id, createddate, modifieddate) VALUES (?, ?, ?)", session["user_id"], now, now)  
        for item in project:
            string = "UPDATE projects SET " + item + " = ? WHERE id = ? AND user_id = ?"
            db.execute(string, project[item], str(new_id), str(session["user_id"]))

        # duplicate project's transformers
        transformers = db.execute("SELECT * FROM transformers WHERE project_id = ?", project_id)
        for transformer in transformers:
            db.execute("INSERT INTO transformers (project_id, power_kva, impedance, type) VALUES (?, ?, ?, ?)", new_id, transformer["power_kva"], transformer["impedance"], transformer["type"])
     
        # flash sucessful message
        flash("Project duplicated", 'alert-primary')
        # return to index page
        return redirect("/")
    
    elif ob == "profile":
        # get referenced profile data from db
        profile = db.execute("SELECT * FROM profiles WHERE id = ? AND user_id = ?", id, session["user_id"])[0]

        # remove non duplicated keys from dict
        del profile["id"]
        del profile["createddate"]
        del profile["modifieddate"]
        
        # add "copy" to name
        profile["name"] += "(copy)"
        
        # create a new entry in db
        new_id = db.execute("INSERT INTO profiles (user_id, createddate, modifieddate) VALUES (?, ?, ?)", session["user_id"], now, now)  
        for item in profile:
            string = "UPDATE profiles SET " + item + " = ? WHERE id = ? AND user_id = ?"
            db.execute(string, profile[item], str(new_id), str(session["user_id"]))
        
        # flash sucessful message
        flash("Profile duplicated", 'alert-primary')
        # return to index page
        return redirect("/profiles")

    # flash error message
    flash("Parameter error", 'alert-danger')
    # return to index page
    return redirect("/")

@app.route("/customers")
@login_required
def customers():

    # get actual user customers
    customersList = db.execute("SELECT id, name, createddate, modifieddate FROM customers WHERE user_id = ? ORDER BY modifieddate DESC", session["user_id"])
    
    # Render customers page
    return render_template("customers.html", customersList=customersList)

@app.route("/customer", methods=["GET", "POST"])
@login_required
def customer():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
     
        # if user have click on delete button
        # get id of user to delete
        delete = request.form.get("delete")
        if delete != None:
            db.execute("DELETE FROM customers WHERE id = ? AND user_id = ?", delete, session["user_id"])
            db.execute("UPDATE projects SET customer_id = NULL WHERE customer_id = ? AND user_id = ?", delete, session["user_id"])
            flash("Customer Deleted", 'alert-primary')
            return redirect("/customers")
            
        parameter_list = ["name", "email", "phone", "zipcode", "state", "city", "street", "district", "number", "complement"]
        
        # get webpage input data
        parameter = {}
        for item in parameter_list:
            parameter[item] = request.form.get(item)
        
        if not parameter["name"]: parameter["name"] = "noname"

        # get customer id
        id = request.form.get("id")

        now = datetime.now()

        # if no id is a new user then create a new entry in db
        if not id:
            id = db.execute("INSERT INTO customers (user_id, createddate) VALUES (?, ?)", session["user_id"], now)
            
        # update customer data
        db.execute("UPDATE customers SET modifieddate = ? WHERE id = ? AND user_id = ?", now, id, session["user_id"])
        for item in parameter_list:
            string = "UPDATE customers SET " + item + " = ? WHERE id = ? AND user_id = ?"
            db.execute(string, parameter[item], str(id), str(session["user_id"]))

        # redirect
        flash(parameter["name"] + " saved", 'alert-primary')
        return redirect("/customers")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        
        # get id if user have click edit on customers page
        id = request.args.get("id")
        customerData = None
        
        # if user have click in edit in customers page
        if id:
            customerData = db.execute("SELECT * FROM customers WHERE id = ? AND user_id = ?", id, session["user_id"])[0]

        return render_template("customer.html", customerData=customerData)

@app.route("/profiles")
@login_required
def profiles():

    profilesList = db.execute("SELECT id, name, createddate, modifieddate FROM profiles WHERE user_id = ? ORDER BY modifieddate DESC", session["user_id"])
    
    # Render customers page
    return render_template("profiles.html", profilesList=profilesList)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
     
        # if user have click on delete button
        # get id of profile to delete
        delete = request.form.get("delete")
        if delete != None:
            db.execute("DELETE FROM profiles WHERE id = ? and user_id = ?", delete, session["user_id"])
            db.execute("UPDATE projects SET profile_id = NULL where profile_id = ? and user_id = ?", delete, session["user_id"])
            flash("Profile Deleted", 'alert-primary')
            return redirect("/profiles")
        
        parameter_list = ["name", "threshold_factor", "n_factor_threshold", "max_n_threshold", "inansi_factor", "iansi_time", "mag_oil_factor", "mag_dry_factor", "trip_factor", "n_trip_factor", "delay_50"]
        
        # get webpage parameters data
        parameter = {}
        for item in parameter_list:
            parameter[item] = request.form.get(item)

        if not parameter["name"]: parameter["name"] = "noname"
        
        # get profile id
        id = request.form.get("id")

        now = datetime.now()

        # if no id is a new profile then create a new entry in db
        if not id:
            id = db.execute("INSERT INTO profiles (user_id, createddate) VALUES (?, ?)", session["user_id"], now)

        # update profile data
        db.execute("UPDATE profiles SET modifieddate = ? WHERE id = ? AND user_id = ?", now, id, session["user_id"])
        for item in parameter_list:
            string = "UPDATE profiles SET " + item + " = ? WHERE id = ? AND user_id = ?"
            db.execute(string, parameter[item], str(id), str(session["user_id"]))

        flash(parameter["name"] + " saved", 'alert-primary')
        return redirect("/profiles")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        
        # get id if user have click edit on profiles page
        id = request.args.get("id")
        profileData = None
        
        # if user have click in edit in customers page
        if id:
            profileData = db.execute("SELECT * FROM profiles WHERE id = ? and user_id = ?", id, session["user_id"])[0]

        return render_template("profile.html", profileData=profileData)

@app.route("/diagram")
@login_required
def diagram():
    # get project id
    id = request.args.get("id")
    
    # pick project data from db (if no one item throws out of range index)
    projectData = db.execute("SELECT id, name, profile_id, tri_sc, bi_sc, lg_sc_max, lg_sc_min, voltage, demand, pf FROM projects WHERE id = ? AND user_id = ?", id, session["user_id"])[0]
    
    # pick profile data from db
    profile_id = projectData["profile_id"]
    # ensures profile exists
    if not profile_id:
        flash("Must provide a profile", 'alert-danger')
        return redirect("project?id=" + id + "&go=project")
    profileData = db.execute("SELECT threshold_factor, n_factor_threshold, max_n_threshold, inansi_factor, iansi_time, mag_oil_factor, mag_dry_factor, trip_factor, n_trip_factor, delay_50 FROM profiles WHERE id = ? AND user_id = ?", profile_id, session["user_id"])[0]

    # pick transformers data from db
    transformersData = db.execute("SELECT id, power_kva, impedance, type FROM transformers WHERE project_id = ?", id)
    # ensures at least 1 transformer exists
    if len(transformersData) == 0:
        flash("Must provide at least 1 transformer", 'alert-danger')
        return redirect("project?id=" + id + "&go=transformers")


    # populate diagramInfo
    diagramInfo = {}
    # add projectData to diagramInfo
    diagramInfo = projectData
    # add profileData to diagramInfo
    diagramInfo.update(profileData)
    
    # populate transformersInfo
    transformersInfo = transformersData
    for transformer in transformersInfo:
        # calculate nominal current
        transformer["in"] = transformer["power_kva"] / ( diagramInfo["voltage"] * sqrt(3) )
        # calculate iansi current
        transformer["iansi"] = ( transformer["in"] * 100 ) / transformer["impedance"]
        # calculate inansi current
        transformer["inansi"] = transformer["iansi"] * diagramInfo["inansi_factor"]
        # calculate magnetization current
        if transformer["type"] == 1:
            transformer["im"] = diagramInfo["mag_dry_factor"] * transformer["in"] 
        elif transformer["type"] == 2:
            transformer["im"] = diagramInfo["mag_oil_factor"] * transformer["in"] 

    # calculate nominal current
    diagramInfo["inom"] = diagramInfo["demand"] / ( diagramInfo["voltage"] * sqrt(3) * diagramInfo["pf"])
    # calculata threshold current
    diagramInfo["i_th"] = diagramInfo["inom"] * diagramInfo["threshold_factor"]
    # calculata neutral threshold current
    diagramInfo["i_th_n"] = diagramInfo["i_th"] * diagramInfo["n_factor_threshold"]
    
    # calculata inrush current
    bigger_im = 0
    tr_id = 0
    # get bigger im
    for transformer in transformersInfo:
        if transformer["im"] > bigger_im: 
            bigger_im = transformer["im"]
            tr_id = transformer["id"]
    sum_in = 0
    # get in summation
    for transformer in transformersInfo:
        if transformer["id"] != tr_id:
            sum_in += transformer["in"]
    diagramInfo["inrush"] = bigger_im + sum_in

    # calculate i_trip
    diagramInfo["i_trip"] = diagramInfo["inrush"] * diagramInfo["trip_factor"]

    # calculate neutral_i_trip
    diagramInfo["i_trip_n"] = diagramInfo["i_trip"] * diagramInfo["n_trip_factor"]

    # calculate time dial
    diagramInfo["time_dial"] = ( ( ( ( diagramInfo["inrush"] / diagramInfo["i_th"] ) ** 2 ) - 1 ) / 80 ) * ( 0.1 + diagramInfo["delay_50"] )

    # iec extremely inverse constants
    k = 80
    alpha = 2
    steps_qty = 300

    # calculate 50/51 phase curve
    step = (diagramInfo["i_trip"] - diagramInfo["i_th"]) / steps_qty
    current = diagramInfo["i_th"] + step
    phase_50_51_curve = []
    while current < diagramInfo["i_trip"]:
        phase_50_51_curve.append( {"x": current, 'y': ( ( k * diagramInfo["time_dial"] ) / ( ( ( current / diagramInfo["i_th"] ) ** alpha ) - 1 ) )} )
        current = phase_50_51_curve[-1]['x'] + step
    phase_50_51_curve[-1]["y"] = 0.01

    # calculate 50/51 neutral curve
    step = (diagramInfo["i_trip_n"] - diagramInfo["i_th_n"]) / steps_qty
    current = diagramInfo["i_th_n"] + step
    neutral_50_51_curve = []
    while current < diagramInfo["i_trip_n"]:
        neutral_50_51_curve.append( {"x": current, 'y': ( ( k * diagramInfo["time_dial"] ) / ( ( ( current / diagramInfo["i_th_n"] ) ** alpha ) - 1 ) )} )
        current = neutral_50_51_curve[-1]['x'] + step
    neutral_50_51_curve[-1]["y"] = 0.01

    # print("diagramInfo", diagramInfo, type(diagramInfo), len(diagramInfo))
    # print("transformersInfo", transformersInfo, type(transformersInfo), len(transformersInfo))
    # print()
    # print("phase_50_51_curve", phase_50_51_curve, type(phase_50_51_curve), len(phase_50_51_curve))
    # print()
    # print("neutral_50_51_curve", neutral_50_51_curve, type(neutral_50_51_curve), len(neutral_50_51_curve))
    
    
    return render_template("diagram.html", diagramInfo=diagramInfo, transformersInfo=transformersInfo, phase_50_51_curve=phase_50_51_curve, neutral_50_51_curve=neutral_50_51_curve)

if __name__ == '__main__':
  webview.start()