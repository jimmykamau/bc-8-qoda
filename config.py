import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['APP_SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    REDIS_URL = os.environ['REDIS_URL']

    SECURITY_RECOVERABLE = True
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = os.environ['APP_PASSWORD_SALT']
    SECURITY_POST_CONFIRM_VIEW = '/login'
    SECURITY_EMAIL_SENDER = "support@winguh.com"
    #SECURITY_CHANGE_URL = '/myaccount'
    #SECURITY_POST_CHANGE_VIEW = '/myaccount'

    MAIL_SERVER = 'mail.winguh.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ['APP_MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']
    MAIL_DEFAULT_SENDER = 'support@winguh.com'


class ProductionConfig(Config):
    DEBUG = False
    REDIRECT_URI = 'http://qoda.apps.winguh.com/oauth2callback'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    REDIRECT_URI = 'http://localhost:5000/oauth2callback'


class TestingConfig(Config):
    TESTING = True
