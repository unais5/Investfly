from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm, UserInfoForm, EditProfileForm , SearchForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import user_login, user_info, wallet, stock
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, send_user_verification_email

import yfinance as yf

@app.route('/')
def home_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("home_page.html")
    # return render_template("base2.html")
    # return render_template("profile.html")
    # return render_template("dashboard.html")

@app.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    user = user_info.query.filter_by(user_id=current_user.id).first_or_404()
    form = EditProfileForm()
    if form.validate_on_submit():
        if user_info.valid_phone_num(form.phone.data):
            user.phone = form.phone.data
            user.addr = form.addr.data
            db.session.commit()
    return render_template('profile.html',user=user,form=form)

@app.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
    search_s = SearchForm()
    search_results = ['', '']
    user = user_info.query.filter_by(id=current_user.id).first_or_404()
    u_wallet = wallet.query.filter_by(user_id=current_user.id).first_or_404()
    
    headings = ['ID', 'Name', 'Previous Closing', 'Transaction Date']
    user_stocks = stock.query.filter_by(user_id=current_user.id).all()
    data = []
    for i in range(len(user_stocks)):
        # user_stocks[i].update_price()
        # db.session.commit()
        data.append(user_stocks[i].get_list())
    # return render_template('dashboard.html', wallet=u_wallet)
    # return render_template("table.html", data=data, headings=headings)
    if search_s.validate_on_submit():
        ticker = yf.Ticker(search_s.search.data)
        ticker_info = ticker.info
        search_results = [search_s.search.data, ticker_info['previousClose'], ticker_info['volume']]
    return render_template('dashboard.html', wallet=u_wallet ,data=data , headings=headings, results=search_results, searches=search_s)


@app.route('/verify_user/<token>', methods = ['GET', 'POST'])
def verify_user(token):
    tid = user_login.query.get(user_login.verify_user_token(token).id)
    user = user_login.query.filter_by(id=tid.id).first_or_404()
    if user:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_information'))
    return redirect(url_for('user', username=user.username))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # return redirect(url_for('home_page'))
        return redirect(url_for('dashboard'))
    form = LoginForm()
    formpwd = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = user_login.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Username or Password incorrect")
            return redirect(url_for('login'))
        login_user(user, remember=False)
        # return render_template("dashboard.html")
        return redirect(request.args.get("next") or url_for('home_page'))
    if formpwd.validate_on_submit():
        user = user_login.query.filter_by(email = formpwd.email.data).first()
        if user:
            send_password_reset_email(user)
            return render_template('plswait.html')
    return render_template('login.html', title='Sign In', form=form,formpwd=formpwd)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = user_login(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        if user:
            send_user_verification_email(user)
            return render_template("plswait.html")
    return render_template('register.html', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = user_login.query.filter_by(username=username).first_or_404()
    userinfo = user_info.query.filter_by(user_id=user.id).first()
    if userinfo and user:
        return render_template('user.html', user=user, userinfo=userinfo)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request(email):
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    # form = ResetPasswordRequestForm()
    # if form.validate_on_submit():
        # user = user_login.query.filter_by(email=form.email.data).first()
    user = user_login.query.filter_by(email).first()
    if user:
        send_password_reset_email(user)
    flash('Check your email for the instructions to reset your password')
    return redirect(url_for('login'))
    # return render_template('plswait.html',title='Reset Password', form=form)
    return render_template('plswait.html',title='Reset Password')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    user = user_login.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home_page'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/user_information', methods=['GET', 'POST'])
@login_required
def user_information():
    form = UserInfoForm()
    if form.validate_on_submit():
        user_wallet = wallet(balance=5000, user_id=current_user.id)
        db.session.add(user_wallet)
        db.session.commit()
        curr_user_info = user_info(fname=form.fname.data, 
                                    phone=form.phone.data, 
                                    acc_num=form.acc_num.data, 
                                    cnic=form.cnic.data, 
                                    addr=form.addr.data,
                                    user_id=current_user.id)
        db.session.add(curr_user_info)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("user_info.html", form=form)