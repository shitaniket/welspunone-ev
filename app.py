from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import mysql.connector
from mysql.connector import Error
import os
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', '12345678')

# MySQL connection details from environment variables
db_config = {
    'user': os.getenv('DB_USER', 'your_username'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'host': os.getenv('DB_HOST', 'your_server.mysql.database.azure.com'),
    'database': os.getenv('DB_NAME', 'your_database'),
}

# Hardcoded credentials
USERNAME = 'admin'
PASSWORD_HASH = generate_password_hash('password')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS vehicles (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        status VARCHAR(50) NOT NULL
                    )
                ''')
                conn.commit()
        finally:
            conn.close()

@app.before_first_request
def initialize():
    init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    vehicles = []
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM vehicles')
                vehicles = cursor.fetchall()
        finally:
            conn.close()
    return render_template('index.html', vehicles=vehicles)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'loggedin' in session:
        if request.method == 'POST':
            action = request.form['action']
            vehicle_name = request.form.get('name')
            vehicle_id = request.form.get('id')
            vehicle_status = request.form.get('status')
            
            conn = get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cursor:
                        if action == 'add' and vehicle_name:
                            cursor.execute('INSERT INTO vehicles (name, status) VALUES (%s, %s)', (vehicle_name, 'Available'))
                        elif action == 'remove' and vehicle_id:
                            cursor.execute('DELETE FROM vehicles WHERE id = %s', (vehicle_id,))
                        elif action == 'change_status' and vehicle_id and vehicle_status:
                            cursor.execute('UPDATE vehicles SET status = %s WHERE id = %s', (vehicle_status, vehicle_id))
                        conn.commit()
                finally:
                    conn.close()
                flash('Action completed successfully', 'success')
            else:
                flash('Error connecting to database', 'danger')
            return redirect(url_for('admin'))
        
        conn = get_db_connection()
        vehicles = []
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM vehicles')
                    vehicles = cursor.fetchall()
            finally:
                conn.close()
        return render_template('admin.html', vehicles=vehicles)
    else:
        flash('You need to log in first', 'warning')
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
            session['loggedin'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
