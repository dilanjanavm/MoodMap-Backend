# instance/config.py
import os
class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'root')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'mysql+mysqlconnector://root:root@localhost/moodmap')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '112233344')

