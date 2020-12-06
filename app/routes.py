from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm, UserInfoForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import user_login, user_info
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, send_user_verification_email


@app.route('/')
def home_page():
    return render_template("home_page.html")

@app.route('/verify_user/<token>', methods = ['GET', 'POST'])
def verify_user(token):
    tid = user_login.query.get(user_login.verify_user_token(token).id)
    user = user_login.query.filter_by(id=tid.id).first_or_404()
    if not user:
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
    # return redirect(url_for('home_page'))
    return redirect(url_for('user', username=user.username))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = user_login.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('user_information'))
    return render_template('login.html', title='Sign In', form=form)


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
        # db.session.add(user)
        # db.session.commit()
        #after registeration shift to dashboard
        return redirect(url_for('home_page'))
    return render_template('register.html', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = user_login.query.filter_by(username=username).first_or_404()
    userinfo = user_info.query.filter_by(user_id=user.id).first_or_404()
    return render_template('user.html', user=user, userinfo=userinfo)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = user_login.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',title='Reset Password', form=form)

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
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = UserInfoForm()
    if form.validate_on_submit():
        curr_user_info = user_info(fname=form.fname.data, 
                                    phone=form.phone.data, 
                                    acc_num=form.acc_num.data, 
                                    cnic=form.cnic.data, 
                                    addr=form.addr.data,
                                    user_id=current_user.id )
        db.session.add(curr_user_info)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template("user_info.html", form=form)