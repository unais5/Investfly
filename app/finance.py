import yfinance as yf
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm, UserInfoForm, EditProfileForm , SearchForm , BuyForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import user_login, user_info, wallet, stock


def search_ticker(name):
    ticker = yf.Ticker(name)
    ticker_info = ticker.info
    return [name, ticker_info['previousClose'], ticker_info['volume']]