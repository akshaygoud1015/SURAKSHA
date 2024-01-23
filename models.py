
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class services(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)

class user_booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('users', backref=db.backref('user_booking', lazy=True))
    booking_date = db.Column(db.Date, nullable=False)
    service_name = db.Column(db.String(255), nullable=False)

    # Establish a relationship with the 'users' table

    def __repr__(self):
        return f"Booking(id={self.id}, user_id={self.user_id}, service_name={self.service_name}, booking_date={self.booking_date})"    

class employees_db(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(255), nullable=False)
    employee_mobile_number = db.Column(db.String(15), nullable=False)
    employee_password = db.Column(db.String(255), nullable=False)
    is_attender = db.Column(db.Boolean, nullable=False)
    salary = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Employee(id={self.id}, employee_name={self.employee_name}, employee_mobile_number={self.employee_mobile_number}, is_attender={self.is_attender})"
    


class attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees_db.id'), nullable=False)
    attender_id = db.Column(db.Integer, db.ForeignKey('employees_db.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('present', 'absent'), default='absent', nullable=False)
    attendance_time = db.Column(db.Time, nullable=False)

    # Establish relationship with the employees table
    employee = relationship('employees_db', foreign_keys=[employee_id], backref='employee_attendance')
    attender = relationship('employees_db', foreign_keys=[attender_id], backref='attender_attendance')

    def __repr__(self):
        return f"Attendance(id={self.id}, employee_id={self.employee_id}, attender_id={self.attender_id}, " \
               f"attendance_date={self.attendance_date}, attendance_time={self.attendance_time} status={self.status})"