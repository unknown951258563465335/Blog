from flask import Flask , render_template ,request
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail


f = open('config.json','r+')
param = json.load(f)["param"]

app = Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = param['sender_email'],
    MAIL_PASSWORD = param['sender_password']
)
mail = Mail(app)
if param['local_server'] == 'True':
    app.config['SQLALCHEMY_DATABASE_URI'] = param['local_url']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = param['public_server']
db = SQLAlchemy(app)

class contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50),nullable=True)


class posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50),nullable=True)
    img = db.Column(db.String(50),nullable=True)

@app.route('/')
def main():
    posts_ = posts.query.filter_by().all()[:param['no_of_posts']]
    return render_template('index.html', param=param,posts_ = posts_)

app.run(debug = True)