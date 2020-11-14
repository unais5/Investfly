from flask import Flask , render_template ,redirect , url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail , Message
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

# app.config["MAIL_SERVER"] = 'smpt.gmail.com'
# app.config["MAIL_PORT"] = 587      
# app.config["MAIL_USERNAME"] = 'unais.virtual@gmail.com'  
# app.config['MAIL_PASSWORD'] = 'CH@MPIONs17'  
# app.config['MAIL_USE_TLS'] = False  
# app.config['MAIL_USE_SSL'] = True 
# mail  = Mail(app)
# s = URLSafeTimedSerializer('Thisisasecret')

class User(db.Model):
    __tablename__ = 'login'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique = True)
    email = db.Column(db.Text , unique = True)
    password = db.Column(db.Text)

    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password

 
@app.route('/')
def home_page():
    return render_template("home_page.html")


@app.route('/login' , methods= ['GET' , 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = request.form['username']
        passw = request.form['password']
        Password = User.query.filter(User.username == user).first()
        if Password :
            if passw == Password.password:
               return render_template('dashboard.html')
            else:
                error = 'Username or Password Is Incorrect'
                return render_template('login.html' ,error = error)
    return render_template('login.html') 

# @app.route('/verify' , methods = ['GET'  ,'POST'])
# def verify():
#     return render_template('verify.html')


@app.route('/register' , methods = ['GET' ,'POST'])
def register():
    error = None
    if request.method == 'POST':
        # email = request.form['email']
        # token = s.dumps(email,salt='email-confirm')
        # msg = Message('Confirm Email' , sender = 'unais.virtual@gmail.com' , recipients = [email])
        # link = url_for('confirm_email' , token = token , _external = True)
        # msg.body = 'Your Verification link is {}'.format(link)
        password = request.form['password']
        password2 = request.form['password2'] 
        if password == password2:
            try:
                user = User(request.form['username'],request.form['email'],request.form['password'])
                db.session.add(user)
                db.session.commit()
                # mail.send(msg)
                # return redirect(url_for('verify'))
                #else part should be here
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                check_username = User.query.filter(User.username == request.form['username']).first()
                if check_username == None:
                    pass
                else:
                    error = 'Username Already Taken'

                check_email = User.query.filter(User.email == request.form['email']).first()
                if check_email == None:
                    pass
                else:
                    error = 'Email Already Registered'
                return render_template("register.html" , error = error)
    return render_template("register.html")

# @app.route('/confirm_email/<token>')
# def confirm_email(token):
#     try:
#         email = s.loads(token, salt = 'email-confirm' , max_age = 3600)
#     except SignatureExpired:
#         return render_template('expiration.html')
#     return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)