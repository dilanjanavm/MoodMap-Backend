from flask import Blueprint, request, jsonify
from app.prediction import predict_emotions, get_prediction_proba
from app.utils import create_response, create_error

main = Blueprint('main', __name__)


@main.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')
    print(text)

    # if not text:
    #     return create_error(status=400)
    #
    # prediction = predict_emotions(text)
    # probability = get_prediction_proba(text)
    #
    # response_data = {
    #     'prediction': prediction,
    #     'probability': probability.tolist()
    # }

    return jsonify({'result': 'Your prediction result'})
