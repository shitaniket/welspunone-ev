from flask import Flask, render_template, request, redirect, url_for, make_response
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM vehicles')
            vehicles = cursor.fetchall()
            conn.close()
        else:
            vehicles = []
            print("Failed to connect to the database.")
    except Exception as e:
        print(f"Error retrieving data: {e}")
        vehicles = []

    return render_template('index.html', vehicles=vehicles)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'password':
            resp = make_response(redirect(url_for('admin')))
            resp.set_cookie('loggedin', 'true')
            return resp
        else:
            return "Invalid credentials, please try again."

    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.cookies.get('loggedin') == 'true':
        if request.method == 'POST':
            action = request.form['action']
            vehicle_name = request.form.get('name')
            vehicle_id = request.form.get('id')
            vehicle_status = request.form.get('status')

            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()

                    if action == 'add':
                        cursor.execute('INSERT INTO vehicles (name, status) VALUES (%s, %s)', (vehicle_name, 'Available'))
                    elif action == 'remove':
                        cursor.execute('DELETE FROM vehicles WHERE id = %s', (vehicle_id,))
                    elif action == 'change_status':
                        cursor.execute('UPDATE vehicles SET status = %s WHERE id = %s', (vehicle_status, vehicle_id))

                    conn.commit()
                    conn.close()
                else:
                    print("Failed to connect to the database.")
                
            except Exception as e:
                print(f"Error handling POST request: {e}")

            return redirect(url_for('admin'))

        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM vehicles')
                vehicles = cursor.fetchall()
                conn.close()
            else:
                vehicles = []
                print("Failed to connect to the database.")
        except Exception as e:
            print(f"Error retrieving data: {e}")
            vehicles = []

        return render_template('admin.html', vehicles=vehicles)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('loggedin', '', expires=0)
    return resp

if __name__ == '__main__':
    app.run(debug=True)
