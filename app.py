from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Initialize Flask app
app = Flask(__name__)

# Configure database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "data.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret')  # Change this in production!
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies', 'json']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # For development only

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)

# Create tables
with app.app_context():
    db.create_all()

# Helper function for responses
def json_response(message, status_code, data=None):
    response = {'message': message}
    if data:
        response.update(data)
    return jsonify(response), status_code

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Validate input
    if not data or 'username' not in data or 'password' not in data:
        return json_response('Username and password are required', 400)

    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return json_response('Username already taken', 400)

    # Create new user
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(
        username=data['username'],
        password=hashed_password,
        email=data.get('email')
    )

    db.session.add(new_user)
    db.session.commit()

    return json_response('User created successfully', 201)

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # Validate input
    if not data or 'username' not in data or 'password' not in data:
        return json_response('Username and password are required', 400)

    # Find user
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return json_response('Invalid credentials', 401)

    # Create access token
    access_token = create_access_token(identity=user.id)
    return json_response('Login successful', 200, {'access_token': access_token})

# Protected endpoint example
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return json_response(
        'Protected route accessed successfully', 
        200, 
        {'user_id': user.id, 'username': user.username}
    )

# Another protected endpoint
@app.route('/user-info', methods=['GET'])
@jwt_required()
def user_info():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })

if __name__ == '__main__':
    app.run(debug=True)