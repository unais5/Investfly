import yfinance as yf
from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm, UserInfoForm, EditProfileForm , SearchForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import user_login, user_info, wallet, stock, ticker_info


def search_ticker(names):
    ticker = yf.Ticker(names)
    return ticker_info( name=names.upper(),
                        price=ticker.info['previousClose'],
                        volume=ticker.info['volume'])