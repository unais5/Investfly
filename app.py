from flask import Flask , render_template ,redirect , url_for,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'login'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    password = db.Column(db.Text) 


@app.route('/')
def index():
    return render_template("base1.html")

@app.route('/home')
def home_page():
    return render_template("home_page.html")

if __name__ == '__main__':
    app.run(debug=True)