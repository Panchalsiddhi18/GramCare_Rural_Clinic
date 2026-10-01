import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gramcare-sih-demo-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///gramcare.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
