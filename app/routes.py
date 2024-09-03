from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.prediction import predict_emotions, get_prediction_proba
from app.utils import create_response, create_error

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User  # Import db from models, not directly from app


main = Blueprint('main', __name__)


users_db = {}

@main.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    data = request.get_json()
    text = data.get('text', '')
    print(text)
    current_user = get_jwt_identity()
    print(current_user)
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

    # Query the user from the database
    user = User.query.filter_by(email=email).first()

    print(user.password, password)
    if user and check_password_hash(user.password, password):
        print('here')
        access_token = create_access_token(identity={'email': user.email})
        return create_response(
            data={'access_token': access_token},
            message='Login successful',
            status=200
        )

    return create_error(
        message='Invalid email or password',
        status=401
    )

