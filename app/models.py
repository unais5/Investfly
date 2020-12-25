from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from hashlib import md5
from time import time
import jwt
from flask import render_template, session, request
from datetime import datetime, timedelta
import yfinance as yf
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(seconds=600)

@login.user_loader
def load_user(id):
    return user_login.query.get(int(id))

owns = db.Table( 'owns',
        db.Column('stock_name', db.String, db.ForeignKey('stock.stock_name'),primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user_login.id'),primary_key=True),
        db.Column('owned_qty', db.Integer,nullable=False),
        db.Column('listed_qty', db.Integer), db.relationship("user_login", foreign_keys=[user_id])
)

listings = db.Table( 'listings',
        db.Column('stock_name', db.String, db.ForeignKey('stock.stock_name'),primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user_login.id'),primary_key=True),
        db.Column('listed_qty', db.Integer)
)

transactions = db.Table( 'transactions',
        db.Column('stock_name', db.String, db.ForeignKey('stock.stock_name'),primary_key=True),
        db.Column('seller_id', db.Integer, db.ForeignKey('user_login.id'),primary_key=True),
        db.Column('quantity', db.Integer, nullable=False),
        db.Column('sale_price', db.Float, nullable=False),
        db.Column('date', db.Date, nullable=False)
)



owns = db.Table( 'owns',
        db.Column('stock_name', db.String, db.ForeignKey('stock.stock_name'),primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user_login.id'),primary_key=True),
        db.Column('owned_qty', db.Integer,nullable=False),
        db.Column('listed_qty', db.Integer)
)


listings = db.Table( 'listings',
        db.Column('stock_name', db.String, db.ForeignKey('stock.stock_name'),primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user_login.id'),primary_key=True),
        db.Column('listed_qty', db.Integer)
)



transactions = db.Table( 'transactions',
        db.Column('stock_name', db.String, db.ForeignKey('stock.stock_name'),primary_key=True),
        db.Column('seller_id', db.Integer, db.ForeignKey('user_login.id'),primary_key=True),
        db.Column('buyer_id', db.Integer , db.ForeignKey('user_login.id'),primary_key=True),
        db.Column('quantity', db.Integer, nullable=False),
        db.Column('sale_price', db.Float, nullable=False),
        db.Column('date', db.Date, nullable=False)
)

################## main schema tables 
class stock(db.Model):
    stock_name = db.Column(db.String, primary_key=True, nullable=False)
    curr_price = db.Column(db.Float, nullable=False)
    vol = db.Column(db.Integer, nullable=False)

    def _repr_(self):
        return '<stock details %r>' % (self.user_id)

class user_login(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    # M:N relationships
    stocks = db.relationship('stock', secondary=owns, lazy='subquery',
                backref=db.backref('users', lazy=True))
    u_listings = db.relationship('stock', secondary=listings, lazy='subquery',
                backref=db.backref('listers', lazy=True))
    bought = db.relationship('stock', secondary=transactions, lazy='subquery',
                backref=db.backref('buyers', lazy=True))
    sold = db.relationship('stock', secondary=transactions, lazy='subquery',
                backref=db.backref('sellers', lazy=True))
    
    # 1:1 relationships
    information = db.relationship('user_info', backref='user_login', lazy=True)
    u_wallet = db.relationship('wallet', backref='user_login', lazy=True)

    def _repr_(self):
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
    name= db.Column(db.String(20))
    phone= db.Column(db.String, unique=True, nullable=False)
    acc_num= db.Column(db.Integer, unique=True, nullable=False)
    cnic= db.Column(db.Integer, unique=True, nullable=False)
    addr= db.Column(db.String(50))

    # 1:1 relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id', ondelete='NO ACTION'),nullable=False)

    def get_list(self):
        return [self.id, self.fname, self.phone, self.cnic]

    def _repr_(self):
        return '<User {}>'.format(self.fname)

    @staticmethod
    def valid_phone_num(phone):
        return phone.isdigit()

class wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    balance = db.Column(db.Float)

    user_id = db.Column(db.Integer, db.ForeignKey('user_login.id', ondelete='CASCADE'), nullable=False)

    def _repr_(self):
        return '<Wallet # {}>'.format(self.id)
        

# class stock(db.Model):
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     stock_name = db.Column(db.String, nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)
#     curr_price = db.Column(db.Float, nullable=False)
#     # transaction_date = db.Column(db.String, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user_login.id',onupdate='CASCADE',ondelete='NO ACTION'), nullable=False)

#     def _repr_(self):
#         return '<Stock # {}>'.format(self.id)
    
#     def update_price(self):
#         ticker = yf.Ticker(self.stock_name)
#         ticker_info = ticker.info
#         self.curr_price = ticker_info['previousClose']
#         return
    
#     def get_list(self):
#         return [ self.stock_name, self.curr_price , self.quantity]
    
#     def get_vol(self):
#         return self.quantity

# class transaction(db.Model):
    # id = db.Column(db.Integer, primary_key=True, nullable=False)
    # transaction_date = db.Column(db.Date, nullable=False)
    # buyer_id = db.Column(db.Integer, nullable=False)
    # quantity = db.Column(db.Integer, nullable=False)
    # seller_id = db.Column(db.Integer, nullable=False)
    # selling_price = db.Column(db.Float, nullable=False)
    # stock_name = db.Column(db.String, db.ForeignKey('stock.stock_name',onupdate='CASCADE',ondelete='NO ACTION'), nullable=False)
    
    # def _repr_(self):
    #     return '<transaction %r>' % (self.user_id)
    
    

# class available_stocks(db.Model):
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     stock_name = db.Column(db.String, db.ForeignKey('stock.stock_name',onupdate='CASCADE'), nullable=False)
#     seller_id = db.Column(db.Integer, db.ForeignKey('user_login.id',onupdate='CASCADE', ondelete='NO ACTION'), nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)
#     curr_price = db.Column(db.Float, db.ForeignKey('stock.curr_price',onupdate='CASCADE', ondelete='NO ACTION'),nullable=False)

#     def _repr_(self):
#         return '<Available Stock # {}>'.format(self.id)
    
#     def get_list(self):
#         return [self.stock_name, self.seller_id, self.curr_price , self.quantity]

#######################

####################### relationship  intermediate models

# admin.add_view(ModelView(user_login, db.session))
# admin.add_view(ModelView(user_info, db.session))
# admin.add_view(ModelView(wallet, db.session))
# admin.add_view(ModelView(stock, db.session))
# admin.add_view(ModelView(transaction, db.session))

class ticker_info():
    def _init_(self, name, volume, price):
        self.name = name
        self.price = price
        self.volume = volume

    def get_vol(self):
        return self.volume

#############^^^^^^^^^^^^^^^^^^^^^^^###############
