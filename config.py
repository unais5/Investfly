import os
import datetime
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_POOL_RECYCLE = 90
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = '' #Enter your Admin Email here
    MAIL_PASSWORD = '' #Enter Admin Email Password here
    ADMINS = [''] #Enter your Admin Email here