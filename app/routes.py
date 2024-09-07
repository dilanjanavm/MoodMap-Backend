from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.prediction import predict_emotions, get_prediction_proba
from app.utils import create_response, create_error

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, EmotionReport, DiaryEntry  # Import db from models, not directly from app
from datetime import datetime

main = Blueprint('main', __name__)


users_db = {}

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


# @main.route('/predict', methods=['POST'])
# @jwt_required()
# def predict():
#     data = request.get_json()
#     text = data.get('text', '')
#     print(text)
#     current_user = get_jwt_identity()
#     print(current_user)
#     if not text:
#         return create_error(status=400)
#
#     prediction = predict_emotions(text)
#     probability = get_prediction_proba(text)
#     print(probability)
#     response_data = {'prediction': prediction, 'probability': probability}
#     print(response_data)
#
#     return create_response(data=response_data, status=200)


@main.route('/predict_details', methods=['POST'])
@jwt_required()
def predict():
    data = request.get_json()
    text = data.get('text', '')
    selected_dairy_date = data.get('selected_dairy_date', '')  # Date from the frontend

    if not text:
        return create_error(message='Text input is required', status=400)

    if not selected_dairy_date:
        return create_error(message='Selected dairy date is required', status=400)

    # Parse the selected diary date
    try:
        diary_date = datetime.strptime(selected_dairy_date, '%Y-%m-%d').date()
    except ValueError:
        return create_error(message='Invalid date format. Use YYYY-MM-DD.', status=400)

    # Perform emotion prediction
    prediction = predict_emotions(text)
    probability = get_prediction_proba(text)

    # Identify the main emotion and its percentage
    main_emotion = max(probability, key=probability.get)
    main_emotion_percentage = probability[main_emotion]

    # Get the current user from the JWT token
    current_user_email = get_jwt_identity()['email']
    user = User.query.filter_by(email=current_user_email).first()

    # Create a new DiaryEntry instance
    new_entry = DiaryEntry(
        user_id=user.id,
        content=text,
        main_emotion=main_emotion,
        main_emotion_percentage=main_emotion_percentage,
        created_at=diary_date  # Save the selected diary date
    )
    db.session.add(new_entry)
    db.session.commit()

    # Save the emotion reports
    for emotion_name, emotion_percentage in probability.items():
        new_emotion_report = EmotionReport(
            diary_id=new_entry.id,
            emotion_name=emotion_name,
            emotion_percentage=emotion_percentage
        )
        db.session.add(new_emotion_report)

    db.session.commit()

    # Prepare the response data
    response_data = {
        'prediction': main_emotion,
        'probability': probability
    }

    return create_response(data=response_data, message='Prediction successful', status=200)


@main.route('/diary-reports', methods=['GET'])
@jwt_required()
def get_diary_reports():

    current_user_email = get_jwt_identity()['email']

    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return create_error(message="User not found", status=404)

    diary_entries = DiaryEntry.query.filter_by(user_id=user.id).all()

    reports = []
    for entry in diary_entries:
        emotion_reports = EmotionReport.query.filter_by(diary_id=entry.id).all()
        report = {
            'id': entry.id,
            'content': entry.content,
            'main_emotion': entry.main_emotion,
            'main_emotion_percentage': entry.main_emotion_percentage,
            'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'emotion_reports': [
                {
                    'emotion_name': emotion.emotion_name,
                    'emotion_percentage': emotion.emotion_percentage
                }
                for emotion in emotion_reports
            ]
        }
        reports.append(report)

    return create_response(data=reports, message="Diary reports fetched successfully", status=200)


@main.route('/diary-reports/<int:diary_id>', methods=['GET'])
@jwt_required()
def get_diary_report_by_id(diary_id):
    # Get the current user from the JWT token
    current_user_email = get_jwt_identity()['email']
    user = User.query.filter_by(email=current_user_email).first()

    if not user:
        return create_error(message="User not found", status=404)

    # Query the diary entry by ID and user ID to ensure the current user is the owner
    diary_entry = DiaryEntry.query.filter_by(id=diary_id, user_id=user.id).first()

    if not diary_entry:
        return create_error(message="Diary entry not found", status=404)

    # Query the associated emotion reports for the diary entry
    emotion_reports = EmotionReport.query.filter_by(diary_id=diary_entry.id).all()

    # Prepare the response data
    response_data = {
        'id': diary_entry.id,
        'content': diary_entry.content,
        'main_emotion': diary_entry.main_emotion,
        'main_emotion_percentage': diary_entry.main_emotion_percentage,
        'created_at': diary_entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'emotion_reports': [
            {
                'emotion_name': report.emotion_name,
                'emotion_percentage': report.emotion_percentage
            }
            for report in emotion_reports
        ]
    }

    return create_response(data=response_data, message="Diary report fetched successfully", status=200)
