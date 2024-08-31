import joblib

pipe_lr = joblib.load(open("./models/emotion_classifier_pipe_lr.pkl", "rb"))


def predict_emotions(text):
    return pipe_lr.predict([text])[0]

def get_prediction_proba(text):
    return pipe_lr.predict_proba([text])