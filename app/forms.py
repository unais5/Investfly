from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, IntegerField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, DataRequired
from app.models import user_login, user_info
from flask import render_template

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = user_login.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Usernmae Already Taken.')

    def validate_email(self, email):
        user = user_login.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email Address Already Registered')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class UserInfoForm(FlaskForm):
    fname = StringField('First Name')
    phone = StringField('Phone Number', validators=[DataRequired()])
    acc_num = StringField('Account Number', validators=[DataRequired()]) 
    cnic = StringField('CNIC', validators=[DataRequired()])
    addr = TextField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')


    def validate_phone(self, phone):
        user = user_info.query.filter_by(phone=phone.data).first()
        if user is not None:
            raise ValidationError('Phone Number Already Registered')
    
    def validate_cnic(self, cnic):
        user = user_info.query.filter_by(cnic=cnic.data).first()
        if user is not None:
            raise ValidationError('CNIC Already Registered')

    def validate_acc_num(self, acc_num):
        user = user_info.query.filter_by(acc_num=acc_num.data).first()
        if user is not None:
            raise ValidationError('Account Number Already Registered')

class EditProfileForm(FlaskForm):
    phone = StringField('Phone Number')
    addr = TextField('Phone Number')
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    search = StringField('Search..')
    submit = SubmitField('Search')

class BuyForm(FlaskForm):
    name = StringField('Stock Name')
    volume = IntegerField('Volume')
    password = StringField('Enter Password')
    submit = SubmitField('Confirm Purchase')

class SellForm(FlaskForm):
    name = StringField('Stock Name')
    volume = IntegerField('Volume')
    sale_price = DecimalField('Sale Price')
    password = StringField('Enter Password')
    submit = SubmitField('Confirm Purchase')