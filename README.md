## SURAKSHA ##
REQUIREMENTS:
1.PYTHON
2.MYSQL
3.ANY CODE EDITOR

LIBRARIES TO INSTALL (UNTIL NOW)

1.flask
2.flask_bcrypt
3.datetime
4.flask_sqlalchemy
5.sqlalchemy.orm

command - pip install flask flask_bcrypt flask_mysqldb

MYSQL DATABASE:

CREATE A DB NAMED "userDB"

TWO TABLES ARE NEEDED TO BE CREATED UP UNTIL NOW

1. "users" table : CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    mobile_number VARCHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL
);
 -- ADD 2 users to the DB manually ; use this command to make one of the users admin :

     ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0;

   and now make one of the users admin using this code :
   
   UPDATE users SET is_admin = 1 WHERE mobile_number = 'admin_mobile_number';  #replace with any one of the user's number

    


2. "services" Table :

   create a table using the following command 

CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL
);

need to manually add the services for now to test  use this command:

INSERT INTO services (name, description, price) VALUES
('Behaviour Modification', 'modifies behaviour', 99.99),
('Speech Therapy', 'Speech therapy for children', 99.99),
('School Readiness', 'School education for children', 99.99),
('Occupational Therapy', 'Occupational therapy for adults', 99.99),
('Group Therapy', 'Group Therapy For Everybody', 49.99),
('Parental Counseling', 'Counseling for parents', 99.99),
('General Guidance', 'General guidance for your needs', 99.99);


.

3."user_booking" table:
    create a user_booking table using the command:

    CREATE TABLE user_booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    service_name VARCHAR(255),
    booking_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) );

Now add few bookings into the table for testings using these commands:
     INSERT INTO user_booking (user_id, service_name, booking_date) VALUES
    (2, 'Group Therapy', '2023-10-09'),
    (3, 'Speech Therapy', '2024-01-15'),
    (4, 'School Readiness', '2023-09-23'),
    (3, 'general guidance', '2023-12-12'),
    (4, 'School Reading', '2023-11-16');

4. "employees_db" table:
    create a employees_db table using the command:

   CREATE TABLE employees_db (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(255) NOT NULL,
    employee_mobile_number VARCHAR(15) NOT NULL,
    employee_password VARCHAR(255) NOT NULL,
    is_attender BOOLEAN NOT NULL
);

   initially add two employees_db for testing using this command:

  INSERT INTO employees_db(employee_name,employee_mobile_number,employee_password,is_attender) VALUES("employee1","1","1",true);
  INSERT INTO employees_db(employee_name,employee_mobile_number,employee_password,is_attender) VALUES("employee2","2","2",false);

5. "attendance" table:
    create attendance table using the command:

   CREATE TABLE attendance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id INT,
        attender_id INT,
        attendance_date DATE,
        status ENUM('present', 'absent') DEFAULT 'absent',
        FOREIGN KEY (employee_id) REFERENCES employees_db(id),
        FOREIGN KEY (attender_id) REFERENCES employees_db(id)
       );

    use this command to add a new column that stores time:

    ALTER TABLE attendance ADD COLUMN attendance_time TIME;
     

#keep updating this file with latest updates .thank you.
