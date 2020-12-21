from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, DataRequired
from app.models import user_login
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
    # lname = StringField('Last Name')
    phone = StringField('Phone Number', validators=[DataRequired()])
    acc_num = StringField('Account Number', validators=[DataRequired()]) 
    cnic = StringField('CNIC', validators=[DataRequired()])
    addr = TextField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Submit')

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
    pwd = StringField('Enter Password')
    submits = SubmitField('Confirm Purchase')