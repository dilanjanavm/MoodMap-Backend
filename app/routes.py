
from app.prediction import predict_emotions, get_prediction_proba
from app.utils import create_response, create_error

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User  # Import db from models, not directly from app


main = Blueprint('main', __name__)


users_db = {}

@main.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')
    print(text)

    if not text:
        return create_error(status=400)

    prediction = predict_emotions(text)
    probability = get_prediction_proba(text)
    print(probability)
    response_data = {'prediction': prediction, 'probability': probability}
    print(response_data)

    return create_response(data=response_data, status=200)


@main.route('/register', methods=['POST'])
def register():
    print(request.json)
    data = request.json
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Username, email, and password are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)

    # Create a new user instance
    new_user = User(username=username, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    hashed_password = users_db.get(email)

    if hashed_password and check_password_hash(hashed_password, password):
        session['user'] = email
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'message': 'Invalid email or password'}), 401

