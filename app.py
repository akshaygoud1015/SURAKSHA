from flask import Flask, jsonify, request, render_template, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from datetime import date, datetime, timedelta
from models import db, users, user_booking, employees_db, attendance, services  # Correct import order
from sqlalchemy.orm import joinedload,Session
import requests
import json
from enum import Enum


app = Flask(__name__)
app.secret_key = 'z8za7m(621a)nnehl-$-+u8dpjb*b_667)i^kj@ght=&6-5#'
bcrypt = Bcrypt(app)

# username='akshaygoud10'
# password='Kabali1015'
# hostname='akshaygoud10.mysql.pythonanywhere-services.com'
# db='akshaygoud10$default'
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="root",
    password="admin",
    hostname="localhost",
    databasename="userDb",
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize db
db.init_app(app)

# Additional configuration or routes...

class ApiClient:
	apiUri = 'https://api.elasticemail.com/v2'
	apiKey = '3D2EB68EC893F4B3CBFF5FA7E9C344FD39B1C09EF54B8BF198824FC34E98029E6804406AFF38BEAAB4531FF45F02A594'

	def Request(method, url, data):
		data['apikey'] = ApiClient.apiKey
		if method == 'POST':
			result = requests.post(ApiClient.apiUri + url, data = data)
		elif method == 'PUT':
			result = requests.put(ApiClient.apiUri + url, data = data)
		elif method == 'GET':
			attach = ''
			for key in data:
				attach = attach + key + '=' + data[key] + '&' 
			url = url + '?' + attach[:-1]
			result = requests.get(ApiClient.apiUri + url)	
			
		jsonMy = result.json()
		
		if jsonMy['success'] is False:
            
			return jsonMy['error']
			
		return jsonMy['data']


def Send(subject, EEfrom, fromName, to, bodyHtml, bodyText, isTransactional):
	return ApiClient.Request('POST', '/email/send', {
		'subject': subject,
		'from': EEfrom,
		'fromName': fromName,
		'to': to,
		'bodyHtml': bodyHtml,
		'bodyText': bodyText,
		'isTransactional': isTransactional})

@app.route("/")
def index():
    return render_template("index.html")




@app.route("/login", methods=['GET', 'POST'])
def login():
    # fetching any messages
    message = request.args.get('message')
    if message:
        return render_template("login.html",message=message)

    if request.method == 'POST':
        mobile_number = request.form['mobile_number']
        password_candidate = request.form['password']

        # Querying the database with SQLAlchemy
        user = users.query.filter_by(mobile_number=mobile_number).first()

        if user:
            password_hash = user.password

            if bcrypt.check_password_hash(password_hash, password_candidate):
                session['user_id'] = user.id

                if user.is_admin:
                    return redirect(url_for("admin_dashboard"))
                else:
                    flash('You are now logged in', 'success')
                    return redirect(url_for('dashboard'))
            else:
                message = "Wrong password"
                return render_template("login.html", message=message)
        else:
            return render_template("login.html", message="User not found. Please check your mobile number")

    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        password = request.form['password']

        # Generating hashed password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            # Creating a new user instance
            new_user = users(name=name, email=email, mobile_number=mobile_number, password=hashed_password)

            # Adding the new user to the database
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login', message="Account created successfully!"))

        except Exception as e:
            print(f"Error creating user: {e}")
            return render_template("signup.html", message="Internal Server Error")

    return render_template("signup.html")

@app.route("/forgot", methods=['GET', 'POST'])
def forgot():
    # fetching details from webpage
    if request.method == 'POST':
        mobile_number = request.form['mobile_number']
        email = request.form['email']

        # fetching mobile number from database
        user = users.query.filter_by(mobile_number=mobile_number).first()

        # checking existence of user
        if user:
            if email == user.email:
                session['user_id'] = user.id
                return redirect(url_for('reset'))
            else:
                return render_template("forgot.html",message="Invalid details")
        else:
            return render_template("forgot.html",message="User not found. Please check your mobile number")
            
    return render_template("forgot.html")

@app.route("/reset", methods=['GET', 'POST'])
def reset():
    # checking user in session
    if 'user_id' in session:
        user_id = session['user_id']
        user = users.query.filter_by(id=user_id).first()
    
    # fetching new password from webpage
    if request.method == 'POST':
        new_password = request.form['password']
        
        try:
            # encrypting new password
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            return redirect(url_for('login',message="Password changed successfully!"))
            
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

    return render_template("reset.html")


@app.route("/bookings")
def bookings():
    user_id = request.args.get('user_id')
    print(user_id)

    # Fetch user details and booking from the database using SQLAlchemy
    user_data = users.query.filter_by(id=user_id).first()
    bookings_data = user_booking.query.filter_by(user_id=user_id).all()
    print(bookings_data)

    return render_template("bookings.html", user_data=user_data, bookings_data=bookings_data)


@app.route("/dashboard")
def dashboard():
    if 'user_id' in session:
        # Fetch user details and services from the database using SQLAlchemy
        user_id = session['user_id']
        user_data = users.query.filter_by(id=user_id).first()
        services_list = services.query.all()

        # Extracting data from the services_list using list comprehension
        service_data = [{
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'price': service.price
        } for service in services_list]

        return render_template("dashboard.html", user_data=user_data, services=service_data)
    else:
        return redirect(url_for('login'))
    
@app.route("/admin_dashboard")
def admin_dashboard():
    # Check if the logged-in user is an admin
    user_id = session['user_id']
    user = users.query.filter_by(id=user_id).first()

    if user and user.is_admin:
        # Admin user
        active_users = users.query.with_entities(users.name, users.mobile_number).all()
        print(active_users)
        return render_template("admin_dashboard.html", users=active_users)
    else:
        return redirect(url_for('login'))
@app.route("/clients")
def clients():
    # Check if the logged-in user is an admin
    user_id = session.get('user_id')
    if user_id is None:
        # Redirect to login if not logged in
        return redirect(url_for('login'))

    user = users.query.filter_by(id=user_id).first()

    if user and user.is_admin:
        # Admin user
        # Calculate the date 3 months ago
        three_months_ago = datetime.now() - timedelta(days=90)

        # Query active clients (booked a service in the last 3 months)
        active_clients = (
            db.session.query(users.name, users.mobile_number, user_booking.booking_date, user_booking.service_name)
            .join(user_booking, users.id == user_booking.user_id)
            .filter(user_booking.booking_date >= three_months_ago)
            .all()
)

        # Query inactive clients (not booked a service in the last 3 months)
        inactive_clients = db.session.query(
            users.name, users.mobile_number, user_booking.booking_date, user_booking.service_name
        ).join(user_booking, users.id == user_booking.user_id).filter(user_booking.booking_date < three_months_ago).all()


        return render_template("clients.html", active_clients=active_clients, inactive_clients=inactive_clients)
    else:
        # Redirect to login if not admin
        return redirect(url_for('login'))

@app.route("/all_bookings")
def all_bookings():
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Fetch upcoming booking
    upcoming_bookings = (
        db.session.query(user_booking, users)
        .join(users)
        .filter(user_booking.booking_date >= current_date)
        .options(joinedload(user_booking.user))
        .all()
    )


    # Fetch previous booking
    previous_bookings = (
        db.session.query(user_booking, users)
        .join(users)
        .filter(user_booking.booking_date < current_date)
        .options(joinedload(user_booking.user))
        .all()
    )

    print(upcoming_bookings, previous_bookings)

    return render_template("all_bookings.html", upcoming_bookings=upcoming_bookings, previous_bookings=previous_bookings)


@app.route("/admin_services")
def admin_services():
    # Query all existing services
    existing_service = services.query.all()
    service_data=[]
    # Convert each service object to a dictionary
    service_data = [{
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'price': service.price
    } for service in existing_service]
    print(service_data)

    return render_template("admin_services.html", existing_service=service_data)


@app.route("/edit_service/<int:service_id>", methods=['POST'])
def edit_service(service_id):
    if request.method == 'POST':
        # Get form data
        new_price = request.form['new_price']

        # Update the service price using SQLAlchemy
        service_to_update = services.query.get(service_id)
        if service_to_update:
            service_to_update.price = new_price
            db.session.commit()

            message = "Updated price successfully"

            return render_template("admin_services.html", message=message)

    return redirect(url_for("admin_services"))


@app.route("/add_service", methods=['POST'])
def add_service():
    if 'user_id' in session:
        # Check if the logged-in user is an admin
        user_id = session['user_id']
        user = users.query.filter_by(id=user_id).first()

        if user and user.is_admin:
            service_name = request.form['service_name']
            description = request.form['description']
            price = request.form['price']

            # Add a new service using SQLAlchemy
            new_service = services(name=service_name, description=description, price=price)
            db.session.add(new_service)
            db.session.commit()

            message = "Added service successfully"

            return render_template("admin_services.html", message=message)

    return redirect(url_for("admin_services"))
@app.route("/remove_service", methods=['POST'])

def remove_service():
    message = ""

    if 'user_id' in session:
        # Check if the logged-in user is an admin
        user_id = session['user_id']
        user = users.query.filter_by(id=user_id).first()

        if user and user.is_admin:
            service_id = request.form['service_id']

            # Delete the service using SQLAlchemy
            service_to_remove = services.query.get(service_id)
            if service_to_remove:
                db.session.delete(service_to_remove)
                db.session.commit()

                message = "Removed the service successfully"

    return render_template("admin_services.html", message=message)


@app.route("/employees")
def employees():

    all_employees = employees_db.query.all()

    employee_data = []

    for employee in all_employees:
        # Calculate the number of days the employee is present in the current month
        current_month_attendance = attendance.query.filter(
            attendance.employee_id == employee.id,
            attendance.attendance_date.between(datetime.now().replace(day=1), datetime.now())
        ).filter_by(status='present').distinct(attendance.attendance_date).all()


        present_days = len(current_month_attendance)

        employee_data.append({
            'name': employee.employee_name,
            'number': employee.employee_mobile_number,
            'password': employee.employee_password,
            'attender': employee.is_attender,
            'salary': employee.salary,
            'present_days': present_days
        })



    return render_template("employees.html",employee_data=employee_data)


@app.route("/add_employee",methods=["POST"])
def add_employee():
        if 'user_id' in session:
            # Check if the user is in session
            user_id = session['user_id']
            user = users.query.filter_by(id=user_id).first()

            # check if the user is admin
            if user and user.is_admin:
                name=request.form['name']
                mobile_number=request.form['mobile_number']
                password=request.form['password']
                attender=request.form['attender']
                salary=request.form['salary']

                if attender=="yes" or "Yes":
                    is_attender=True
                else:
                    is_attender=False        

                new_employee = employees_db(employee_name=name,employee_mobile_number=mobile_number, employee_password=password,is_attender=is_attender,salary=salary)
                db.session.add(new_employee)
                db.session.commit()    

                message="Succesfully added a new employee!"
                return render_template("employees.html", message=message)

        return render_template("employees.html")

@app.route("/remove_employee", methods=["POST"])
def remove_employee():

    if 'user_id' in session:
        user_id = session['user_id']
        user = users.query.filter_by(id=user_id).first()

        # Check if the logged-in user is an admin
        if user and user.is_admin:
            employee_name = request.form['employee_name']

            # Delete the employee using SQLAlchemy
            employee_to_remove = employees_db.query.filter_by(employee_name=employee_name).first()
            if employee_to_remove:
                db.session.delete(employee_to_remove)
                db.session.commit()

                message = f"Removed the employee {employee_name} successfully"
                return render_template("employees.html", message=message)
                
            else:
                message = f"No employee found with name {employee_name}"
                return render_template("employees.html", message=message)

    return render_template("employees.html")

@app.route("/staff", methods=["GET", "POST"])
def staff():
    if request.method == "GET":
        return render_template("staff_login.html", error_message=None)
    else:
        mobile_number = request.form["mobile_number"]
        password = request.form["password"]

        # Check if the mobile number is present in the employees table
        user = employees_db.query.filter_by(employee_mobile_number=mobile_number).first()

        if user:
            # Mobile number is found, check password
            if user.employee_password == password:
                # Password is correct

                # Store user details in the session
                session["user_details"] = {
                    "id": user.id,
                    "employee_name": user.employee_name,
                    "employee_mobile_number": user.employee_mobile_number,
                    "is_attender": user.is_attender
                }

                if user.is_attender:
                    # user is an attender, redirect to attender page
                    return redirect(url_for("attender"))
                else:
                    # user is a regular employee, redirect to employee page
                    return redirect(url_for("employee"))
            else:
                # Incorrect password
                message = "Wrong password"
                return render_template("staff_login.html", message=message)
        else:
            # user not found
            message = "Employee not found. Please check your mobile number."
            return render_template("staff_login.html", message=message)
        

@app.route("/attender", methods=["POST", "GET"])
def attender():
    user_details = session.get("user_details")
    details = list(user_details.values())
    attender_id = details[0]

    if not user_details or user_details.get("is_attender") != 1:
        # Redirect if the user is not in session or is not an attender
        return redirect(url_for("employee"))

    today = date.today()
    # Query present employees for today
    present_employees = employees_db.query.join(attendance, employees_db.id == attendance.employee_id).filter(
        (attendance.attender_id == attender_id) & (attendance.attendance_date == today) & (attendance.status == 'present')
    ).distinct(employees_db.employee_name).all()

    print(present_employees)

    # Query all employees
    employees_list = employees_db.query.all()
    message = None

    if request.method == "POST":
        marked_ids = request.form.getlist("marked_ids")
        print(marked_ids)
        attendance_date = date.today()

        # Mark attendance for selected employees
        for employee_id in marked_ids:
            existing_attendance = attendance.query.filter(
                (attendance.employee_id == employee_id) & (attendance.attender_id == attender_id) &
                (attendance.attendance_date == attendance_date)
            ).first()

            if existing_attendance:
                existing_attendance.status = 'present'
            else:
                new_attendance = attendance(employee_id=employee_id, attender_id=attender_id,
                                            attendance_date=attendance_date, status='present')
                db.session.add(new_attendance)

        db.session.commit()
        message = "Marked attendance for today"

    return render_template("attender.html", user_details=details, employees=employees_list,
                           present_employees=present_employees, message=message)


@app.route("/employee")
def employee():
    user_details = session.get("user_details")
    details = list(user_details.values())
    print(details)

    if not user_details or user_details.get("is_attender") != 0:
        return redirect(url_for("attender"))

    # You can add more logic for the employee dashboard here
    return render_template("employee.html", user_details=details)


@app.route("/make_booking",methods=["GET","POST"])
def make_booking():
    if request.method=="POST":
        
        user_name = request.args.get('user_name')
        user_email=request.args.get('user_mail')
        user_service=request.args.get('service')
        booking_date=request.form["book_date"]
        user_data=[user_name,user_email,user_service,booking_date]
        user_q=users.query.filter_by(email=user_email).first()
        user_id=user_q.id
        
        new_booking=user_booking(user_id=user_id,booking_date=booking_date,service_name=user_service)
        db.session.add(new_booking)
        db.session.commit()
        email_subject = "Booking Confirmation"
        email_from = "20r01a67c2@cmritonline.ac.in"
        email_from_name = "Suraksha"
        email_to = user_email

        # Email content with user details
        email_body_html = f"""
            <h1>Booking Details</h1>
            <p>Name: {user_name}</p>
            <p>Email: {user_email}</p>
            <p>Service Booked: {user_service}</p>
            <p>Date: {booking_date}</p>
        """
        email_body_text = "Booking details:\n\n" + \
                           f"Name: {user_name}\n" + \
                           f"Email: {user_email}\n" + \
                           f"Service Booked: {user_service}\n" + \
                           f"Date: {booking_date}\n"

        Send(email_subject, email_from, email_from_name, email_to, email_body_html, email_body_text, True)

  
        message="Booked a session succesfully , Please check your mail(spam too) for booking confirmation"


        return render_template("make_booking.html",user_data=user_data,message=message) 

    user_name = request.args.get('user_name')
    user_email=request.args.get('user_email')
    user_number=request.args.get('user_number')
    user_service=request.args.get('user_service')
    current_date = datetime.now().strftime('%Y-%m-%d')
    service_price=services.query.filter(services.name==user_service).first()
    if service_price:
        price=service_price.price
    
    user_data=[user_name,user_email,user_number,user_service,price,current_date]


   

    return render_template("make_booking.html",user_data=user_data)


    




@app.route("/signout")

def signout():
    
    session.clear()

    return redirect(url_for('login'))




if __name__ == '__main__':


    # Run the Flask application in debug mode
    app.run(debug=True)
    