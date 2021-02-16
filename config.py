import os

from flask_settings import BasicConfig


class Config(BasicConfig):
    APPLICATION_ROOT = os.path.dirname(os.path.abspath(__file__)).replace('settings', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = 'the test random string'
    JWT_SECRET_KEY = 'the jwt random string'
    JSONIFY_MIMETYPE = 'application/json'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APPLICATION_ROOT, 'app.db')
