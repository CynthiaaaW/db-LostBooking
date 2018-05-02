from flask import Flask, render_template, request, session, url_for, redirect
import hashlib
import pymysql.cursors
import time

app = Flask(__name__)
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       port=8889,
                       db='flight_ticket_system',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/register")
def register():
    return render_template('register.html')

# Authenticates the register
@app.route('/registerAuth/<userType>', methods=['GET', 'POST'])
def registerAuth(userType):
    username = request.form['email']
    password = request.form['password']
    password = calc_md5(password)
    cursor = conn.cursor()
    
    query = 'SELECT * FROM ' + userType + ' WHERE email = %s'
    cursor.execute(query, (username))
    
    data = cursor.fetchone()
    error = None
    
    if (data):
        error = "This user already exists"
        return render_template('register.html', error=error)
    else:
       if userType == "customer":
           name = request.form['name']
           buildingNo = request.form['buildingNo']
           street = request.form['street']
           city = request.form['city']
           state = request.form['state']
           phoneNum = request.form['phoneNum']
           passportNo = request.form['passportNo']
           passportExp = request.form['passportExp']
           passportCty = request.form["passportCty"]
           dateOfBirth = request.form['dateOfBirth']
           ins = 'INSERT INTO customer(email, name, password, building_number, street, city, state, phone_number, \
	 				passport_number, passport_expiration, passport_country, date_of_birth) VALUES(%s, %s, %s, %s, %s, %s, %s, \
	 				%s, %s, %s, %s, %s)'
           cursor.execute(ins, (username, name, password, buildingNo, street, city, state, phoneNum, passportNo, passportExp, passportCty, dateOfBirth))
       elif userType == "booking_agent":
           booking_agent_id = request.form['bookingAgentId']
           ins = 'INSERT INTO booking_agent (email, password, booking_agent_id) VALUES(%s, %s, %s)'
           cursor.execute(ins, (username, password, booking_agent_id))
       else:
           fname = request.form['fname']
           lname = request.form['lname']
           dateOfBirth = request.form['dateOfBirth']
           airline_name = request.form['airline_name']
           ins = 'INSERT INTO airline_staff(email, password, first_name, last_name, date_of_birth, airline_name) \
           	    VALUES(%s, %s, %s, %s, %s, %s)'
           cursor.execute(ins, (username, password, fname, lname, dateOfBirth, airline_name))
       conn.commit()
       cursor.close()
       return render_template('index.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    password = request.form['password']
    userType = request.form['usertype']
    password = calc_md5(password)
    
    cursor = conn.cursor()
    if (userType == "airline_staff"):
        query = 'SELECT * FROM  airline_staff WHERE username = %s and password = %s'
    else:
        query = 'SELECT * FROM ' + userType + ' WHERE email = %s and password = %s'
    
    cursor.execute(query, (username, password))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if (data == False):
        error = 'Invalid login. Did you register?'
        return render_template('login.html', error=error)
    else:
        session['username'] = username
        session['type'] = userType
        return redirect(url_for('home'))
			

@app.route('/home')
def home():
     username = session['username']
     user = session['type']
     return render_template(user + '.html', username=username)

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')

def calc_md5(password):
    m = hashlib.md5()
    m.update(password.encode(encoding = 'utf-8'))
    return m.hexdigest()

@app.route('/homesearch', methods=['GET', 'POST'])
def home_search():
    departure_airport = request.form['Departure Airport']
    departure_city = request.form['Departure City']
    arrival_airport = request.form['Arrival Airport']
    arrival_city = request.form['Arrival City']
    date = request.form['Date']
    
    cursor = conn.cursor()
    
    print(date > now())
    
    if date < now():
        return render_template('overdue.html')
    else:
        if len(departure_airport) > 0 and len(arrival_airport) > 0:
            airport = 'SELECT * FROM flight WHERE departure_airport = %s AND arrival_airport = %s AND date(departure_time) = %s'
            cursor.execute(airport, (departure_airport, arrival_airport, date))
        
        elif len(departure_airport) > 0 and len(arrival_airport) == 0:
            airport = 'SELECT * FROM flight WHERE departure_airport = %s AND date(departure_time) = %s AND arrival_airport = (SELECT airport_name FROM airport WHERE airport_city = %s)'
            cursor.execute(airport, (departure_airport, date, arrival_city))
           
        elif len(departure_airport) == 0 and len(arrival_airport) > 0:
            airport = 'SELECT * FROM flight WHERE arrival_airport = %s AND date(departure_time) = %s AND departure_airport = (SELECT airport_name FROM airport WHERE airport_city = %s)'
            cursor.execute(airport, (arrival_airport, date, departure_city))
           
        else:
            airport = 'SELECT * FROM flight WHERE date(departure_time) = %s AND departure_airport = (SELECT airport_name FROM airport WHERE airport_city = %s) and \
            arrival_airport = (SELECT airport_name FROM airport WHERE airport_city = %s)'
            cursor.execute(airport, (date, departure_city, arrival_city))
    
        data = cursor.fetchall()
        cursor.close()
        print(data)
        return render_template('search.html', result = data)



def now():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
     

@app.route('/search', methods=['GET', 'POST'])
def search():
    cursor = conn.cursor()
    cursor.close()
    return render_template('index.html')

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    ticket_id = request.form['Ticket ID']
    customer_email = request.form['Email']
    
    cursor = conn.cursor()
    ticket = 'SELECT ticket_id FROM ticket WHERE ticket_id = %s'
    cursor.execute(ticket, (ticket_id))
    data1 = cursor.fetchall()
    buyer = 'SELECT customer_email FROM purchases WHERE ticket_id = %s'
    cursor.execute(buyer, (ticket_id))
    data2 = cursor.fetchall()
    print(data1)
    print(data2)
    email = 'SELECT email FROM customer WHERE email = %s'
    cursor.execute(email, (customer_email))
    data3 = cursor.fetchall()
    print(data3)
    print(data1 is not None)
    print(customer_email not in data2)
    print(customer_email in data3)
    
    if (data1 is not None) and (customer_email not in data2) and (data3 is not None):
        purchase = "INSERT INTO purchases VALUES (%s,%s,'dummy', NOW())"
        cursor.execute(purchase, (ticket_id, customer_email))
        conn.commit()
        cursor.close()
        return render_template('purchase_successful.html')
    else:
        return render_template('purchase.html')
    
@app.route('/purchasepage', methods=['GET', 'POST'])
def purchasepage():
    return render_template('purchase.html')

@app.route('/homepage', methods=['GET', 'POST'])
def back_to_home():
    return render_template('index.html')

@app.route('/viewflight', methods=['GET', 'POST'])
def view_flight():
    cursor = conn.cursor()
    
    all_flight = "SELECT * FROM flight WHERE status = 'UPCOMING'"
    cursor.execute(all_flight)
    
    data = cursor.fetchall()
    cursor.close()
    print(data)
    return render_template('showallflight.html', result = data)
    

    
app.secret_key = 'b\xef\xe2\xca\';sI\xd0a\xca\x8f\x92\x83\xf74\x1b\x9c\x80\x99\x15c\xa5\xad\xab'

if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
