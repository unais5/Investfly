from flask_mail import Message
from app import mail
from flask import render_template
from app import app
from threading import Thread


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[InvestFly] Reset Your Password',
                sender= 'investflycorporation@gmail.com',
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html',user=user, token=token))

def send_user_verification_email(user):
    token = user.get_verify_user_token()
    send_email('[InvestFly] Welcome to InvestFly!',
                sender= 'investflycorporation@gmail.com',
               recipients=[user.email],
               text_body=render_template('email/welcome.txt',user=user, token=token),
               html_body=render_template('email/welcome.html',user=user, token=token))


def send_purchase_email(user, stock_data, bill, wallet):
    send_email('[InvestFly]Purchase Confirmed!',
                sender= 'investflycorporation@gmail.com',
               recipients=[user.email],
               text_body=render_template('email/conf_purchase.txt',user=user, stock=stock_data, bill=bill, wallet=wallet),
               html_body=render_template('email/conf_purchase.html',user=user,  stock=stock_data,bill=bill, wallet=wallet))
                                        

def send_listing_email(user, stock_data):
    send_email('[InvestFly]Listing Confirmed!',
                sender= 'investflycorporation@gmail.com',
               recipients=[user.email],
               text_body=render_template('email/conf_listing.txt',user=user,stock=stock_data),
               html_body=render_template('email/conf_listing.html',user=user, stock=stock_data))

def send_sale_email(user, buyer, t_id, stock):
    send_email('[InvestFly]Sale Confirmed!',
                sender= 'investflycorporation@gmail.com',
               recipients=[user.email],
               text_body=render_template('email/conf_sale.txt',user=user, buyer=buyer, transaction_id=t_id , stock=stock),
               html_body=render_template('email/conf_sale.html',user=user ,buyer=buyer, transaction_id=t_id, stock=stock))



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()