from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt
from flask import render_template, session
from datetime import datetime, timedelta

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(seconds=50)

@login.user_loader
def load_user(id):
    return user_login.query.get(int(id))


################## main schema tables 
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


class user_info(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'),unique=True, nullable=False)
    fname= db.Column(db.String(20))
    # lname= db.Column(db.String(20))
    phone= db.Column(db.Integer, unique=True, nullable=False)
    acc_num= db.Column(db.Integer, unique=True, nullable=False)
    cnic= db.Column(db.Integer, unique=True, nullable=False)
    addr= db.Column(db.String(50))
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'),unique=True, nullable=False)
    

    def __repr__(self):
        return '<User {}>'.format(self.fname)

class wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    balance = db.Column(db.Float)

    def __repr__(self):
        return '<Wallet # {}>'.format(self.id)

class stock(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    stock_name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    curr_price = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id'), unique=True, nullable=False)

    def __repr__(self):
        return '<Stock # {}>'.format(self.id)

class transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)
    buyer_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), unique=True, nullable=False)
    
    def __repr__(self):
        return '<Transaction # {}>'.format(self.id)

# class available_stock(db.Model):
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), unique=True, nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)
#     curr_price = db.Column(db.Float, nullable=False)

#     def __repr__(self):
#         return '<Available Stock # {}>'.format(self.id)

#######################

####################### relationship  intermediate models
available_stocks = db.Table('available_stocks',
    db.Column('stock_id', db.Integer, db.ForeignKey('stock.id'), primary_key=True),
    db.Column('seller_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
    db.Column('quantity', db.Integer, nullable=False),
    db.Column('curr_price', db.Float, nullable=False) )




