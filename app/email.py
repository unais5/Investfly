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
            #    remove text body - NEVERMIND DONT REMOVE PHAT JAEGA
               html_body=render_template('email/reset_password.html',user=user, token=token))

def send_user_verification_email(user):
    token = user.get_verify_user_token()
    send_email('[InvestFly] Welcome to InvestFly!',
                sender= 'investflycorporation@gmail.com',
               recipients=[user.email],
               text_body=render_template('email/welcome.txt',user=user, token=token),
            #    remove text body - NEVERMIND DONT REMOVE PHAT JAEGA
               html_body=render_template('email/welcome.html',user=user, token=token))


def send_purchase_email(user, stock_data, bill, wallet):
    token = user.get_verify_user_token()
    send_email('[InvestFly]Confirm your purchase',
                sender= 'investflycorporation@gmail.com',
               recipients=[user.email],
               text_body=render_template('email/conf_purchase.txt',user=user, token=token, stock=stock_data, bill=bill, wallet=wallet),
            #    remove text body - NEVERMIND DONT REMOVE PHAT JAEGA
               html_body=render_template('email/conf_purchase.html',user=user, token=token, stock=stock_data,bill=bill, wallet=wallet))
                                         
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()