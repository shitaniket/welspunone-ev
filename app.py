from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
db_initialized = False

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

def init_db():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(255) NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
        else:
            print("Failed to connect to the database.")
    except Error as e:
        print(f"Error initializing database: {e}")

@app.before_request
def initialize():
    global db_initialized
    if not db_initialized:
        init_db()
        db_initialized = True

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
            print("Failed to retrieve data from the database.")
    except Error as e:
        print(f"Error fetching data: {e}")
        vehicles = []
    return render_template('index.html', vehicles=vehicles)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'loggedin' in session:
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
                
            except Error as e:
                print(f"Error performing action: {e}")
            
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
                print("Failed to retrieve data from the database.")
        except Error as e:
            print(f"Error fetching data: {e}")
            vehicles = []
        
        return render_template('admin.html', vehicles=vehicles)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # For simplicity, we're using hardcoded credentials.
        # In a real application, use a proper authentication mechanism.
        if username == 'admin' and password == 'password':
            session['loggedin'] = True
            return redirect(url_for('admin'))
        else:
            return "Invalid credentials, please try again."

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
