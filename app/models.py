from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import render_template
from datetime import datetime

# class User(UserMixin, db.Model):
class user_login(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)   
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return user_login.query.get(id)
    
    def get_verify_user_token(self, expires_in=600):
        return jwt.encode(
            {'verify_user': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_user_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['verify_user']
        except:
            return
        return user_login.query.get(id)

@login.user_loader
def load_user(id):
    return user_login.query.get(int(id))

class user_info(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'), nullable=False)
    fname= db.Column(db.String(20))
    # lname= db.Column(db.String(20))
    phone= db.Column(db.Integer, nullable=False)
    acc_num= db.Column(db.Integer, nullable=False)
    cnic= db.Column(db.Integer, nullable=False)
    addr= db.Column(db.String(50))
    

    def __repr__(self):
        return '<Post {}>'.format(self.fname)