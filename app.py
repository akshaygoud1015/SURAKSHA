from flask import Flask, jsonify, request , render_template , redirect, session , url_for ,  flash
from flask_restful import Resource, Api
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from datetime import date, datetime , timedelta

app = Flask(__name__)
app.secret_key = 'z8za7m(621a)nnehl-$-+u8dpjb*b_667)i^kj@ght=&6-5#' 
bcrypt = Bcrypt(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'userDB'
mysql = MySQL(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile_number = request.form['mobile_number']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE mobile_number = %s", (mobile_number,))
        print(result)
        
        if result > 0:
            print(result)
            data = cur.fetchone()
            password = data[4]

            if bcrypt.check_password_hash(password, password_candidate):
                print("found")
                # Password is correct, set the user ID in the session
                session['user_id'] = data[0]

                if data[5]:
                    return redirect(url_for("admin_dashboard"))
                else:
                    
                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))  # Redirect to the dashboard route or wherever you want to go after login
            else:
                # Incorrect password
                message="wrong password"
                return render_template("login.html",message=message)
        else:
            # User not found
            flash('Invalid mobile number', 'danger')

    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile_number=request.form['mobile_number']
        password = request.form['password']


        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password)

        # Store the user details in the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, mobile_number, password) VALUES (%s, %s, %s, %s)", (name, email, mobile_number, hashed_password))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template("signup.html")


@app.route("/reset", methods=['GET',"PSOT"])

def reset():
    return render_template("reset.html")

@app.route("/bookings")

def bookings():
    user_id = request.args.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cur.fetchone()
    
    cur.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
    bookings_data = cur.fetchall()

    return render_template("bookings.html", user_data=user_data, bookings_data=bookings_data)

@app.route("/dashboard")
def dashboard():
    if 'user_id' in session:
        # User is authenticated, render the dashboard

        # Fetch user details from the database using the user_id stored in the session
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cur.fetchone()

        cur.execute("SELECT * FROM services")
        services=cur.fetchall()

        return render_template("dashboard.html", user_data=user_data, services=services)
    else:
        # User is not authenticated, redirect to login page
        return redirect(url_for('login'))
    

@app.route("/admin_dashboard")
def admin_dashboard():
            # Check if the logged-in user is an admin
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
        is_admin = cur.fetchone()[0]
        if is_admin:
    # Admin user
    # Query active users and their bookings, and pass the data to the template
    # Modify the query according to your database structure
            cur.execute("SELECT name,mobile_number FROM users ")
            active_users = cur.fetchall()
            print(active_users)
            return render_template("admin_dashboard.html",users=active_users)

@app.route("/clients")
def clients():
    
    # Check if the logged-in user is an admin
    user_id = session.get('user_id')
    if user_id is None:
        # Redirect to login if not logged in
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
    is_admin = cur.fetchone()[0]

    if is_admin:
        # Admin user
        # Calculate the date 3 months ago
        three_months_ago = datetime.now() - timedelta(days=90)

        # Query active clients (booked a service in the last 3 months)
        cur.execute("SELECT users.name, users.mobile_number,bookings.booking_date,bookings.service_name FROM users JOIN bookings ON users.id = bookings.user_id WHERE bookings.booking_date >= %s", (three_months_ago,))
        active_clients = cur.fetchall()
        print("active",active_clients)

        # Query inactive clients (not booked a service in the last 3 months)
        cur.execute("SELECT users.name, users.mobile_number,bookings.booking_date,bookings.service_name FROM users JOIN bookings ON users.id = bookings.user_id WHERE bookings.booking_date <= %s", (three_months_ago,))
        inactive_clients = cur.fetchall()
        print(inactive_clients)

        return render_template("clients.html", active_clients=active_clients, inactive_clients=inactive_clients)
    else:
        # Redirect to login if not admin
        return redirect(url_for('login'))

@app.route("/all_bookings")
def all_bookings():
    current_date = datetime.now().strftime('%Y-%m-%d')
    cur = mysql.connection.cursor()

# Fetch upcoming bookings
    cur.execute("SELECT * FROM bookings WHERE booking_date >= %s", (current_date,))
    upcoming_bookings = cur.fetchall()
    cur.execute("SELECT * FROM bookings WHERE booking_date <= %s", (current_date,))
    previous_bookings = cur.fetchall()

    print(upcoming_bookings,previous_bookings)


    return render_template("all_bookings.html",upcoming_bookings=upcoming_bookings,previous_bookings=previous_bookings)


@app.route("/admin_services")

def admin_services():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM services")
    existing_services = cur.fetchall()
    print(existing_services)


    return render_template("admin_services.html",existing_services=existing_services)


@app.route("/edit_service/<int:service_id>", methods=['POST'])
def edit_service(service_id):
    if request.method == 'POST':
        # Get form data
        new_price = request.form['new_price']
        cur=mysql.connection.cursor()

        # Update the service price in the database
        cur.execute("UPDATE services SET price = %s WHERE id = %s", (new_price, service_id))
        mysql.connection.commit()
        message="updated price succesfully"

        # Redirect back to the admin dashboard
        return render_template("admin_services.html",message=message)



@app.route("/add_service", methods=['POST'])
def add_service():
        if 'user_id' in session:
            # Check if the logged-in user is an admin
            user_id = session['user_id']
            cur = mysql.connection.cursor()
            cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
            is_admin = cur.fetchone()[0]

            if is_admin:
                # Admin user, handle the form submission
                service_name = request.form['service_name']
                description = request.form['description']
                price = request.form['price']

                # Insert the new service into the services table
                cur.execute("INSERT INTO services (name, description, price) VALUES (%s, %s, %s)", (service_name, description, price))
                mysql.connection.commit()

                message="Added service succesfully"

        return render_template("admin_services.html",message=message)

@app.route("/remove_service", methods=['POST'])

def remove_service(): 
            if 'user_id' in session:
                # Check if the logged-in user is an admin
                user_id = session['user_id']
                cur = mysql.connection.cursor()
                cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
                is_admin = cur.fetchone()[0]

                if is_admin:
                    service_id=request.form['service_id']
                    cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
                    mysql.connection.commit()

                    message="removed the service succesfully"
            return render_template("admin_services.html",message=message)        

@app.route("/employees")
def employees():
    return render_template("employees.html")

@app.route("/staff", methods=["GET", "POST"])
def staff():
    if request.method == "GET":
        return render_template("staff_login.html", error_message=None)
    else:
        mobile_number = request.form["mobile_number"]
        password = request.form["password"]

        # Check if the mobile number is present in the employees table
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM employees WHERE employee_mobile_number = %s", (mobile_number,))
        user = cur.fetchone()

        if user:
            # Mobile number is found, check password
            if user[3] == password:
                # Password is correct

                # Store user details in the session
                session["user_details"] = {
                    "id": user[0],
                    "employee_name": user[1],
                    "employee_mobile_number": user[2],
                    "is_attender": user[4]
                }

                if user[4] == 1:
                    # User is an attender, redirect to attender page
                    return redirect(url_for("attender"))
                else:
                    # User is a regular employee, redirect to employee page
                    return redirect(url_for("employee"))
            else:
                # Incorrect password
                message = "Wrong password"
                return render_template("staff_login.html", message=message)
        else:
            # User not found
            message = "Employee not found. Please check your mobile number."
            return render_template("staff_login.html", message=message)


@app.route("/attender",methods=["POST","GET"])
def attender():
    user_details = session.get("user_details")
    details=list(user_details.values())
    attender_id=details[0]

    if not user_details or user_details.get("is_attender") != 1:
        # Redirect if the user is not in session or is not an attender
        return redirect(url_for("employee"))

    cur = mysql.connection.cursor()
    today = date.today()
    cur.execute("SELECT DISTINCT e.employee_name FROM employees e "
                "JOIN attendance a ON e.id = a.employee_id "
                "WHERE a.attender_id = %s AND a.attendance_date = %s AND a.status = 'present'",
                (attender_id, today))
    present_employees = cur.fetchall()
    print(present_employees)
    
    cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()
    message=None

    if request.method == "POST":
    # Handle attendance marking
        marked_ids = request.form.getlist("marked_ids")
        print(marked_ids)
        attendance_date = date.today()       

        for employee_id in marked_ids:
            # Insert or update attendance record
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO attendance (employee_id, attender_id, attendance_date, status) VALUES (%s, %s, %s, 'present') ON DUPLICATE KEY UPDATE status='present'", (employee_id, attender_id, attendance_date))
            mysql.connection.commit()
            message="marked attendance for today"



    return render_template("attender.html", user_details=details,employees=employees,present_employees=present_employees,message=message)

@app.route("/employee")
def employee():
    user_details = session.get("user_details")
    details=list(user_details.values())  # Debug statement
    print(details)


    if not user_details or user_details.get("is_attender") != 0:
        # Redirect if the user is not in session or is not a regular employee
        return redirect(url_for("attender"))

    # You can add more logic for the employee dashboard here
    return render_template("employee.html", user_details=details)


@app.route("/signout")

def signout():
    
    session.clear()

    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)