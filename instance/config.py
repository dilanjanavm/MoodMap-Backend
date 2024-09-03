# instance/config.py
import os
class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'root')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 'mysql+mysqlconnector://root:root@localhost/moodmap')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other configuration settings as needed

