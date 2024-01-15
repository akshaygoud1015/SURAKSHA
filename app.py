from flask import Flask, jsonify, request , render_template , redirect, session , url_for ,  flash
from flask_restful import Resource, Api
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from datetime import datetime , timedelta

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




    
@app.route("/signout")

def signout():
    
    session.clear()

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)