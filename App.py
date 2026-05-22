import os
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='../static', static_url_path='')

# Configuration
app.secret_key = "super_secret_key_change_this_in_production"

# Local MySQL Workbench connection parameters
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:velmurugan2002@127.0.0.1:3306/auth_system_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model (Crash-proofed Datetime Default & Hashing Space)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) # Expanded to store scrypt keys cleanly
    role = db.Column(db.String(20), default='user')  
    join_date = db.Column(db.DateTime, default=datetime.now) # Using safe runtime assignment

# Serve the frontend files from the static folder
@app.route('/')
def index():
    return app.send_static_file('login.html')

# 1. POST /register
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Missing required fields"}), 400
            
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 409
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 409

        # Generate modern scrypt encryption string securely
        hashed_password = generate_password_hash(data['password'], method='scrypt')
        
        role = 'admin' if 'admin' in data['email'].lower() else 'user'
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User registered successfully"}), 201
        
    except Exception as e:
        # Prints runtime blockers directly onto the terminal stack window
        print("\n!!! DATABASE OPERATION CRASH !!!\n", str(e), "\n")
        return jsonify({"error": "Internal server configuration issue"}), 500

# 2. POST /login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Missing username or password"}), 400
            
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({"error": "Invalid username or password"}), 401

        # Store user information in Flask Session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        return jsonify({"message": "Login successful"}), 200
    except Exception as e:
        print("\n!!! LOGIN ROUTE CRASH !!!\n", str(e), "\n")
        return jsonify({"error": "Server failed to process login request"}), 500

# 3. GET /logout
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

# 4. GET /dashboard-data
@app.route('/dashboard-data', methods=['GET'])
def dashboard_data():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access"}), 401
        
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    all_users = []
    if user.role == 'admin':
        all_users = [{"username": u.username, "email": u.email, "role": u.role} for u in User.query.all()]

    return jsonify({
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "join_date": user.join_date.strftime('%Y-%m-%d %H:%M:%S'),
        "all_users": all_users
    }), 200

# 5. GET /profile
@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized access"}), 401
        
    user = User.query.get(session['user_id'])
    return jsonify({
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "join_date": user.join_date.strftime('%Y-%m-%d')
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Generates and tracks database mappings
    # Set fallback host for flawless browser sync tracking
    app.run(host='127.0.0.1', port=5000, debug=True)
