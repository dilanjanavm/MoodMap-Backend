from flask import Blueprint, request, jsonify,session
from app.prediction import predict_emotions, get_prediction_proba
from app.utils import create_response, create_error
from werkzeug.security import generate_password_hash, check_password_hash

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
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if email in users_db:
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    users_db[email] = hashed_password
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

