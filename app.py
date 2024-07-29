from flask import Flask, render_template, redirect, url_for, session
from dotenv import load_dotenv
import os
import mysql.connector

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set secret key from environment variable
app.secret_key = os.getenv('SECRET_KEY')

# Database configuration
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

# Function to get vehicle data from the database
def get_vehicles():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, status FROM vehicles')
    vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    return vehicles

@app.route('/')
def index():
    vehicles = get_vehicles()
    return render_template('index.html', vehicles=vehicles)

@app.route('/login')
def login():
    # This is a placeholder for actual login logic
    session['loggedin'] = True
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
