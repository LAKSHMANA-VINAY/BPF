from flask import Flask, render_template, request, redirect, flash,session
import mysql.connector
from datetime import datetime


app = Flask(__name__)
app.secret_key = '@A*Laxman!@$#12!^&77HG'

config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'mydb'
}

connection = mysql.connector.connect(**config)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register_user')
def register_user():
    return render_template("register_user.html")

@app.route("/user_login",methods=['GET', 'POST'])
def user_login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['pwd']
        type = request.form['type']
        if type=="None":
            return render_template("index.html",msg="Enter Correct Details")
        else:
            try:
                cursor = connection.cursor()
                if type=="user":
                    cursor.execute("SELECT * FROM covid_users WHERE email = %s and password = %s", (email, password))
                elif type=="admin":
                    cursor.execute("SELECT * FROM covid_admin WHERE email = %s and password = %s", (email, password))
                user = cursor.fetchone()

                if user:
                    session['email'] = email
                    if type=="user":
                        return redirect('/after_login')
                    else:
                        return redirect('/after_admin_login')
                else:
                    return render_template('index.html',msg="Your credentials are Wrong")

            except Exception as e:
                return render_template('register_user.html',msg="Something went wrong. Please try again")

            finally:
                cursor.close()

@app.route('/after_admin_login',methods=['GET', 'POST'])
def after_admin_login():
    if 'email' not in session:
        return redirect('/')
    if request.method=='POST':
        search_query=request.form['search_query']
        if len(search_query)==0:
            centers=get_admin_centers()
        else:
            centers=search_admin_centers(search_query)
    else:
        centers=get_admin_centers()
    return render_template('after_admin_login.html',centers=centers)

def get_admin_centers():
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM covid_centers")
    centers = cursor.fetchall()
    cursor.close()
    return centers

def search_admin_centers(search_query):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM covid_centers WHERE name LIKE %s", ('%' + search_query + '%',))
    centers = cursor.fetchall()
    cursor.close()
    return centers

@app.route("/delete_center",methods=['GET','POST'])
def delete_center():
    if request.method=='POST':
        id=request.form['id']
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM covid_centers WHERE id=%s", (id,))
            connection.commit() 
            return redirect('/after_admin_login')
        except Exception as e:
            return render_template('after_admin_login.html',msg="Something went wrong. Please try again")
        
        finally:
            cursor.close()
    return render_template('after_admin_login.html')

@app.route("/add_centers",methods=['GET','POST'])
def add_centers():
    return render_template("add_centers.html")

@app.route("/add",methods=['GET','POST'])
def add():
    if request.method=='POST':
        name=request.form['name']
        place=request.form['place']
        time=request.form['time']
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM covid_centers WHERE name = %s and place=%s ", (name,place))
            user = cursor.fetchone()

            if user:
                return render_template('add_centers.html',msg="Center already exists")

            else:
                cursor.execute("INSERT INTO covid_centers (name, place, time) VALUES (%s, %s, %s)", 
                            (name, place, time))
                connection.commit()
                return render_template('add_centers.html',msg="Center Added successfully")

        except Exception as e:
            return render_template('add_centers.html',msg="Something went wrong. Please try again")

        finally:
            cursor.close()
    return render_template('index.html',msg="Something went wrong. Please try again")

@app.route("/get_details")
def get_details():
    if 'email' in session:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT count(*) as count, center, place FROM covid_book GROUP BY center, place")
            details = cursor.fetchall()
            return render_template("get_details.html", details=details)

        except Exception as e:
            return render_template('after_admin_login.html', msg="Something went wrong. Please try again")

        finally:
            cursor.close()
    return render_template('index.html', msg="Please log in to access this page")


        

@app.route("/after_login", methods=['GET', 'POST'])
def after_login():
    if 'email' not in session:
        return redirect('/')
    if request.method == 'POST':
        search_query = request.form['search_query']
        if len(search_query)==0:
            centers=get_all_centers()
        else:
            centers = search_centers(search_query)
    else:
        centers = get_all_centers()
    return render_template('after_login.html', centers=centers)

def search_centers(search_query):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM covid_centers WHERE name LIKE %s", ('%' + search_query + '%',))
    centers = cursor.fetchall()
    cursor.close()
    return centers

def get_all_centers():
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM covid_centers")
    centers = cursor.fetchall()
    cursor.close()
    return centers

@app.route("/book_slot",methods=['GET','POST'])
def book_slot():
    if request.method=="POST" and 'email' in session:
        name=request.form['name']
        place=request.form['place']
        my_list=[name,place,session['email']]
        current_date = datetime.now()
        formatted_date = current_date.strftime("%d/%m/%Y")
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT count(*) as count FROM covid_book where center=%s and place=%s and date = %s", (name,place,formatted_date))
            count = cursor.fetchone()
            if count:
                count=count[0]
                my_list.append(10-count)
            else:
                my_list.append(10)
        except Exception as e:
            return render_template('after_login.html',msg="Something went wrong. Please try again")
        
        finally:
            cursor.close()

        return render_template("book_slot.html",details=my_list)
    
@app.route("/book",methods=['GET','POST'])
def book():
    if request.method=='POST':
        name=request.form['name']
        place=request.form['place']
        center=request.form['center']
        email=request.form['email']
        phone=request.form['phone']
        current_date = datetime.now()
        formatted_date = current_date.strftime("%d/%m/%Y")
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT count(*) as count FROM covid_book where center=%s and place=%s and date = %s", (center,place,formatted_date))
            count = cursor.fetchone()
            if count[0]>=10:
                return render_template('after_login.html',msg="Slots Completed For Today")
            else:
                cursor.execute("INSERT INTO covid_book (email, name, phone_number,center,place,date) VALUES (%s, %s, %s, %s, %s, %s)", 
                            (email,name, phone, center, place,formatted_date))
                connection.commit()
                return redirect('/history')

        except Exception as e:
            return render_template('after_login.html',msg="Something went wrong. Please try again")

        finally:
            cursor.close()

@app.route("/history")
def history():
    if 'email' in session:
        email=session['email']
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM covid_book where email=%s", (email,))
            details = cursor.fetchall() 
            return render_template("user_history.html",details=details)
        
        except Exception as e:
            return render_template('after_login.html',msg="Something went wrong. Please try again")
        finally:
            cursor.close()
    return redirect('/')



@app.route("/user_register", methods=['GET', 'POST'])
def user_register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        gender = request.form['gender']
        if gender == "-1":
            return render_template('register_user.html',msg="Enter Correct Inputs")
        else:
            age = request.form['age']
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM covid_users WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user:
                    return render_template('register_user.html',msg="User already exists")

                else:
                    cursor.execute("INSERT INTO covid_users (email, password, name, phone_number, gender, age) VALUES (%s, %s, %s, %s, %s, %s)", 
                                (email, password, name, phone, gender, age))
                    connection.commit()
                    return render_template('index.html',msg="Account created successfully")

            except Exception as e:
                return render_template('register_user.html',msg="Something went wrong. Please try again")

            finally:
                cursor.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
