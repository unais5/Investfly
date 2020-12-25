from flask import render_template, flash, redirect, url_for, request , jsonify
from app import app, db 
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm, UserInfoForm, EditProfileForm , SearchForm , BuyForm, SellForm
from flask_login import current_user, login_user, login_required, logout_user
from app.models import user_login, user_info, wallet, stock , ticker_info , available_stocks , transaction
from werkzeug.urls import url_parse
from app.email import send_password_reset_email, send_user_verification_email, send_purchase_email ,send_listing_email, send_sale_email
import yfinance as yf
from app.finance import search_ticker
from datetime import *
from sqlalchemy.sql import func
from sqlalchemy import *
import random

@app.route('/admin')
def admin():
    return render_template("admin.index")

@app.route('/editListing/<stk>/<pr>/<qt>' ,methods = ['GET' , 'POST'])
@login_required
def editListing(stk,pr,qt):
    if request.method == 'POST':
        qty = request.form['volume']
        pwd = request.form['password']
        user_data = user_login.query.filter_by(id=current_user.id).first()

        if user_data and user_data.check_password(pwd):
            seller_listing = available_stocks.query.filter_by(seller_id=current_user.id, stock_name=stk).first()
            seller_portfolio = stock.query.filter_by(stock_name=stk, user_id=current_user.id).first()

            if seller_listing:    
                if int(qty) == 0:
                    db.session.delete(seller_listing)
                    db.session.commit()
                    return redirect(url_for('dashboard'))
                elif int(qty) <= seller_portfolio.quantity:
                    seller_listing.quantity = qty
                    db.session.commit()
                    return redirect(url_for('dashboard'))
                elif int(qty) > seller_portfolio.quantity:
                    flash('Insufficient units. Please enter a valid quantity')
                    return redirect(url_for('editListing',stk=stk,pr=pr,qt=qt))
            else:
                #cannot edit a listing you dont have
                return redirect(url_for('dashboard'))
        else:
            flash("Incorrect password! ")
            return redirect(url_for('editListing',stk=stk,pr=pr,qt=qt))
    return render_template("editListing.html", s_name=stk, s_price=pr)        

@app.route('/buyListing/<stk>/<nm>/<pr>/<qt>' ,methods = ['GET' , 'POST'])
@login_required
def buyListing(stk,nm,pr,qt):
    if request.method == 'POST':
        qty = request.form['volume']
        pwd = request.form['password']
        user_data = user_login.query.filter_by(id=current_user.id).first()
        buy_stock = ticker_info(name=stk,
                                volume=int(qty),
                                price=float(pr))
        
        if user_data:
            if user_data.check_password(pwd): # if the user is valid & entered correct pwd
                bill = float(pr) * float(qty)

                seller_obj = user_login.query.filter_by(username=nm).first()
                seller_id = seller_obj.id
                if seller_id != current_user.id:

                    seller_wallet = wallet.query.filter_by(user_id=seller_id).first()
                    buyer_wallet = wallet.query.filter_by(user_id=current_user.id).first()
                    
                    seller_portfolio = stock.query.filter_by(stock_name=stk, user_id=seller_id).first()
                    seller_listing = available_stocks.query.filter_by(seller_id=seller_id, stock_name=stk).first()

                    if bill <= buyer_wallet.balance and qty <= qt and seller_listing and seller_portfolio:
                        buyer_wallet.balance = buyer_wallet.balance - bill
                        seller_wallet.balance = seller_wallet.balance + bill

                        seller_portfolio.quantity = seller_portfolio.quantity - int(qty)
                        seller_listing.quantity = seller_listing.quantity - int(qty)
                        db.session.commit()

                        if seller_portfolio.quantity <= 0:
                            db.session.delete(seller_portfolio)
                            db.session.commit()
                        if seller_listing.quantity <= 0:
                            db.session.delete(seller_listing)
                            db.session.commit()
                        
                        buyer_portfolio = stock.query.filter_by(stock_name=stk, user_id=current_user.id).first()
                        if buyer_portfolio:
                            buyer_portfolio.quantity = buyer_portfolio.quantity + int(qty)
                            buyer_portfolio.curr_price = pr
                            st_id = buyer_portfolio.id
                            db.session.commit()
                        else:
                            add_to_portfolio = stock(stock_name=stk,
                                                        quantity=int(qty),
                                                        curr_price=float(pr),
                                                        user_id=current_user.id)
                            st_id= add_to_portfolio.id
                            db.session.add(add_to_portfolio)
                            db.session.commit()
                        
                        curr_trns = transaction(transaction_date=date.today(),
                                                buyer_id=current_user.id,
                                                seller_id=seller_id,
                                                quantity=qty,
                                                selling_price=float(pr),
                                                stock_name=stk)
                        db.session.add(curr_trns)
                        db.session.commit()

                        send_purchase_email(user_data, buy_stock, bill, buyer_wallet.balance)
                        send_sale_email(seller_obj, user_data, curr_trns.id, buy_stock)
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Insufficient Balance or quantity out of bounds ")
                        return redirect(url_for('buy',s_name=stk, s_price=pr))
                else:
                    flash("Cannot purchase from self!")
                    return redirect(url_for('dashboard'))
            else:
                flash("Incorrect password!")
                return redirect(url_for('buy',s_name=stk, s_price=pr))
    return render_template("peerbuy.html", stock=stk, stk_price=pr)

@app.route('/history' , methods = ['GET' , 'POST'])
def history():
    headings = ['Name' , 'Seller ID ' , 'Buyer ID' , 'Volume' , 'Price' , 'Date']
    sold = transaction.query.filter_by(seller_id=current_user.id).all()
    print(sold.seller_id)


@app.route('/stocks', methods = ['GET' , 'POST'])
@login_required
def stocks():
    headings = ['ID', 'Name', 'Sale Price' ,'Volume']
    sell_s = available_stocks.query.filter((available_stocks.seller_id>current_user.id) | (available_stocks.seller_id<current_user.id)).all()
    sell_stocks = []
    for i in range(len(sell_s)):
        sell_stocks.append(sell_s[i].get_list())
        sell_stocks[i][1] = user_login.query.filter_by(id=sell_s[i].seller_id).first().username
    return render_template('stock.html' , data=sell_stocks , headings=headings)


@app.route('/myListings', methods = ['GET' , 'POST'])
@login_required
def myListings():
    headings = ['ID', 'Name', 'Sale Price' ,'Volume']
    sell_s = available_stocks.query.filter_by(seller_id=current_user.id).all()

    sell_stocks = []
    for i in range(len(sell_s)):
        sell_stocks.append(sell_s[i].get_list())
        sell_stocks[i][1] = user_login.query.filter_by(id=sell_s[i].seller_id).first().username
    return render_template('myListings.html' , data=sell_stocks , headings=headings)

@app.route('/sell/<s_name>/<s_price>' ,methods = ['GET' , 'POST'])
@login_required
def sell(s_name,s_price):
    to_sell = s_name
    user_data = user_login.query.filter_by(id=current_user.id).first()
    if request.method == 'POST':
        s_price = float(s_price)
        vol =int( request.form['volume'] )
        pwd = request.form['password']
        
        sell_ticker = ticker_info(name=to_sell,
                                    volume=vol,
                                    price=s_price)

        if user_data and user_data.check_password(pwd):
            #if THIS user has THIS stock 
            user_stock_exists = stock.query.filter_by(stock_name=to_sell, user_id=current_user.id).first()
            if user_stock_exists:
                if user_stock_exists.quantity >= vol:
                    ### user_stock_exists.quantity = user_stock_exists.quantity - vol
                    # check ifTHIS user has put THIS share up for sale before as well
                    stk_exists = available_stocks.query.filter_by(stock_name=to_sell, seller_id=current_user.id).first()
                    if stk_exists:
                        if (stk_exists.quantity + vol) <= user_stock_exists.quantity:
                            stk_exists.quantity = stk_exists.quantity + vol
                            stk_exists.curr_price = s_price
                            db.session.commit()
                            send_listing_email(user_data, sell_ticker)
                            return redirect(url_for('dashboard'))
                    else:
                        if vol <= user_stock_exists.quantity:
                            new_stk_sale = available_stocks(stock_name=to_sell,
                                                            seller_id=current_user.id,
                                                            quantity=vol,
                                                            curr_price=s_price)
                            db.session.add(new_stk_sale)
                            db.session.commit()
                            send_listing_email(user_data, sell_ticker)
                            return redirect(url_for('dashboard'))
                else:
                    flash("You don't have sufficient stock")
                    return redirect(url_for('sell',s_name=s_name, s_price=s_price))
            else:
                flash("You dont own shares of this stock")
                return redirect(url_for('sell',s_name=s_name, s_price=s_price))
        else:
                flash("Incorrect Password")
                return redirect(url_for('sell',s_name=s_name, s_price=s_price))
    return render_template("sell.html", s_name=s_name, s_price=s_price)



@app.route('/buy/<s_name>/<s_price>', methods = ['GET' , 'POST'])
@login_required
def buy(s_name,s_price):
    if s_name == "name":
        return redirect(url_for("dashboard"))
    buy = BuyForm()
    if buy.validate_on_submit():
        user_data = user_login.query.filter_by(id=current_user.id).first()
        if user_data and user_data.check_password(buy.password.data): # if the user is valid & entered correct pwd
            buy_stock = search_ticker(s_name)
            buy_stock.volume = buy.volume.data
            bill = buy_stock.price * buy_stock.volume
            user_wallet = wallet.query.filter_by(user_id=current_user.id).first()
            if bill <= user_wallet.balance:
                user_wallet.balance = user_wallet.balance - bill
                db.session.commit()
                stock_exists = stock.query.filter_by(stock_name=s_name, user_id=current_user.id).first()
                if stock_exists:
                    stock_exists.quantity = stock_exists.quantity + buy_stock.volume
                    stock_exists.curr_price = buy_stock.price
                    db.session.commit()
                else:
                    add_stock = stock(stock_name=s_name, 
                                    quantity=buy_stock.volume,
                                    curr_price=buy_stock.price,
                                    user_id=current_user.id)
                    db.session.add(add_stock)
                    db.session.commit()
                curr_trns = transaction(transaction_date=date.today(),
                                            buyer_id=current_user.id,
                                            seller_id=1111,
                                            quantity=buy_stock.volume,
                                            selling_price=buy_stock.price,
                                            stock_name=s_name)
                db.session.add(curr_trns)
                db.session.commit()
                send_purchase_email(user_data, buy_stock, bill, user_wallet.balance)
                return redirect(url_for('dashboard'))
            else:
                flash("Insufficient Balance in your wallet")
                return redirect(url_for('buy',s_name=s_name, s_price=s_price))
        else:
                flash("Incorrect Password")
                return redirect(url_for('buy',s_name=s_name, s_price=s_price))
    return render_template("buy.html", buy=buy, s_name=s_name, s_price=s_price)

@app.route('/')
def home_page():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("home_page.html")

@app.route('/portfolio', methods = ['GET' , 'POST'])
@login_required
def portfolio():
    headings = ['Name', 'Previous Closing' ,'Volume']
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
    search_results = ["name" , "price" , "volume"]
    user = user_info.query.filter_by(id=current_user.id).first()
    u_wallet = wallet.query.filter_by(user_id=current_user.id).first()
    
    u_wallet.balance = "{:.2F}".format(u_wallet.balance)

    shares = db.session.query(func.sum(stock.quantity)).filter(stock.user_id==current_user.id).scalar()
    if not shares:
        shares = 0
    db.session.commit()
    
    headings = [ 'Name', 'Previous Closing','Qty']
    user_stocks = stock.query.filter_by(user_id=current_user.id).all()
    data = []
    assets = 0
    for i in range(len(user_stocks)):
        data.append(user_stocks[i].get_list())
        assets = assets + (user_stocks[i].curr_price * user_stocks[i].quantity)
    assets = "{:.2F}".format(assets)
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
    if tid:
        user = user_login.query.filter_by(id=tid.id).first_or_404()
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('user_information'))
    else:
        unverified = user_login.query.filter(user_login.id != user_info.user_id).scalar()
        if unverified:
            for i in range(len(unverified)):
                db.session.delete(unverified[i])
                db.session.commit()
        return render_template("linkexpired.html")
    
        


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
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
            u_info = user_info.query.filter_by(user_id=user.id).first()
            if u_info:
                login_user(user, remember=False)
            else:
                login_user(user, remember=False)
                return redirect(url_for('user_information'))
            all_stocks = stock.query.all()
            for i in range(len(all_stocks)):
                all_stocks[i].update_price()
                db.session.commit()
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
        if form.username.data == 'admin':
            flash("Username not available")
            return redirect(url_for('register'))

        u_id = random.randint(4000,7000)
        check_id = user_info.query.filter_by(user_id=u_id).first()
        # check_id = user_login.query.filter_by(id=u_id).first()
        while check_id is not None:
            u_id = random.randint(4000,7000)
            check_id = user_login.query.filter_by(id=u_id).first()

        user = user_login(id=u_id, 
                        username=form.username.data, 
                        email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        if user:
            send_user_verification_email(user)
            return render_template("plswait.html")
    return render_template('register.html', form=form)

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
        
        curr_user_info = user_info(fname=form.fname.data, 
                                    phone=form.phone.data, 
                                    acc_num=form.acc_num.data, 
                                    cnic=form.cnic.data, 
                                    addr=form.addr.data,
                                    user_id=current_user.id)
        db.session.add(curr_user_info)
        db.session.commit()
        
        user_wallet = wallet(balance=15000, user_id=current_user.id)
        db.session.add(user_wallet)
        db.session.commit()
        return redirect(url_for('home_page'))
    return render_template("user_info.html", form=form)