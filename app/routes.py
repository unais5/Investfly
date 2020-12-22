from flask import render_template, flash, redirect, url_for, request , jsonify
from app import app, db 
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm, UserInfoForm, EditProfileForm , SearchForm , BuyForm, SellForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import user_login, user_info, wallet, stock , ticker_info , available_stocks
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, send_user_verification_email, send_purchase_email
import yfinance as yf
from app.finance import search_ticker
from datetime import *
from sqlalchemy.sql import func
from sqlalchemy import *

@app.route('/admin')
def admin():
    return render_template("admin.index")


@app.route('/stocks', methods = ['GET' , 'POST'])
@login_required
def stocks():
    headings = ['ID', 'Name', 'Sale Price' ,'Volume']
    sell_s = available_stocks.query.filter_by().all()

    sell_stocks = []
    for i in range(len(sell_s)):
        sell_stocks.append(sell_s[i].get_list())
    return render_template('stock.html' , data=sell_stocks , headings=headings)

@app.route('/sell<s_name>' ,methods = ['GET' , 'POST'])
@login_required
def sell(s_name):
    to_sell = SellForm()
    to_sell.name = s_name
    if to_sell.validate_on_submit():
        user_data = user_login.query.filter_by(id=current_user.id).first()
        sell_ticker = ticker_info(name=to_sell.name,
                                    volume=to_sell.volume,
                                    price=to_sell.sale_price)
        if user_data and user_data.check_password(to_sell.password.data):
            #if THIS user has THIS stock 
            user_stock_exists = stock.query.filter_by(stock_name=s_name, user_id=current_user.id).first()
            if user_stock_exists:
                # does he have sufficient quantity of this stock?
                if str(user_stock_exists.quantity ) < str(sell_ticker.volume):
                    user_stock_exists.quantity = int(str(user_stock_exists.quantity) - str(sell_ticker.volume))
                    # sell_stock_exists = available_stocks.query.filter_by(stock_name=s_name, user_id=current_user.id).first()
                    # if sell_stock_exists:
                    #     sell_stock_exists.quantity = sell_stock_exists.quantity + to_sell
                    # stock_for_sale = available_stocks(stock_name=user_stock_exists.stock_name,
                    #                                         seller_id=current_user.id,
                    #                                         quantity=user_stock_exists.get_vol(),
                    #                                         curr_price=to_sell.sale_price.data)
                    # db.session.add(stock_for_sale)
                    # db.session.commit()
                    return str( user_stock_exists.quantity)
                else:
                    return str( "not sold" )
        # has_stock = stock.query.filter_by(user_id=current_user.id).first()
        return str(has_stock)
    return render_template("sell.html", sell=to_sell)

# @app.route('/user/<username>')
# @login_required
# def user(username):
#     user = user_login.query.filter_by(username=username).first_or_404()
#     userinfo = user_info.query.filter_by(user_id=user.id).first()
#     if userinfo and user:
#         return render_template('user.html', user=user, userinfo=userinfo)

@app.route('/buy', methods = ['GET' , 'POST'])
@login_required
def buy():
    buy = BuyForm()
    if buy.validate_on_submit():
        user_data = user_login.query.filter_by(id=current_user.id).first()
        if user_data and user_data.check_password(buy.password.data): # if the user is valid & entered correct pwd
            buy_stock = search_ticker(buy.name.data)
            buy_stock.volume = buy.volume.data
            bill = buy_stock.price * buy_stock.volume
            user_wallet = wallet.query.filter_by(user_id=current_user.id).first()
            if bill < user_wallet.balance:
                user_wallet.balance = user_wallet.balance - bill
                stock_exists = stock.query.filter_by(stock_name=buy_stock.name, user_id=current_user.id).first()
                if stock_exists:
                    stock_exists.quantity = stock_exists.quantity + buy_stock.volume
                    stock_exists.curr_price = buy_stock.price
                else:
                    add_stock = stock(stock_name=buy_stock.name, 
                                    quantity=buy_stock.volume,
                                    curr_price=buy_stock.price,
                                    user_id=current_user.id)
                    db.session.add(add_stock)
                db.session.commit()
                send_purchase_email(user_data, buy_stock, bill, user_wallet.balance)
                return redirect(url_for('dashboard'))
            else:
                flash("Insufficient Balance in your wallet")
                return redirect(url_for('buy'))
    return render_template("buy.html", buy=buy)

@app.route('/')
def home_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("home_page.html")

@app.route('/portfolio', methods = ['GET' , 'POST'])
@login_required
def portfolio():
    headings = ['ID', 'Name', 'Previous Closing' ,'Volume']
    user_stocks = stock.query.filter_by(user_id=current_user.id).all()
    data = []
    for i in range(len(user_stocks)):
        # user_stocks[i].update_price()
        # db.session.commit()
        data.append(user_stocks[i].get_list())
    return render_template('portfolio.html' , data=data , headings=headings)


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
    
    u_wallet.balance = "{:.2F}".format(u_wallet.balance)

    assets = db.session.query(func.sum(stock.curr_price)).filter(stock.user_id==current_user.id).scalar()
    assets = "{:.2F}".format(assets)
    shares = db.session.query(func.sum(stock.quantity)).filter(stock.user_id==current_user.id).scalar()
    db.session.commit()
    
    headings = ['ID', 'Name', 'Previous Closing']
    user_stocks = stock.query.filter_by(user_id=current_user.id).all()
    data = []
    for i in range(len(user_stocks)):
        data.append(user_stocks[i].get_list())
    if search_s.validate_on_submit():
        ticker_info = search_ticker(search_s.search.data)
        search_results = [ticker_info.name, ticker_info.price, ticker_info.volume]
    return render_template('dashboard.html', wallet=u_wallet,
                            data=data , headings=headings, 
                            results=search_results,
                            searches=search_s, assets=assets,
                            shares=shares)


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
        username = form.username.data
        password = form.password.data
        if username == 'admin' and password == 'test123':
            return redirect(url_for('admin'))
        else:
            user = user_login.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash("Username or Password incorrect")
                return redirect(url_for('login'))
            login_user(user, remember=False)
            #### UNCOMMENT LATER THIS IS USEFUL CODE
            # user_stocks = stock.query.filter_by(user_id=current_user.id).all()
            # for i in range(len(user_stocks)):
            #     user_stocks[i].update_price()
            #     db.session.commit()
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