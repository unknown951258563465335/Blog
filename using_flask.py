from flask import Flask , render_template ,request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import math
from werkzeug.utils import secure_filename

from flask_mail import Mail

f = open('config.json','r+')
param = json.load(f)["param"]

app = Flask(__name__)
app.secret_key = "super-secret-key"
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
app.config['UPLOAD_FOLDER'] = param['upload_location']

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


# @app.route('/')
# def main():
#     posts_ = posts.query.filter_by().all()[:param['no_of_posts']]
#     return render_template('index.html', param=param,posts_ = posts_)

@app.route("/")
def main():
    post = posts.query.filter_by().all()
    last = math.ceil(len(post)/int(param['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts_ = post[(page-1)*int(param['no_of_posts']):(page-1)*int(param['no_of_posts'])+ int(param['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    
    return render_template('index.html', param=param, posts_=posts_, prev=prev, next=next)
# @app.route('/index')
# def Home():
#     posts_ = posts.query.filter_by().all()
#     return render_template('index.html', param=param , posts_=posts_)

@app.route("/dashboard" , methods = ['GET' , 'POST'])
def dashboard():
    if 'user' in session and session['user'] == param['login_username']:
        post = posts.query.all()
        return render_template("dashboard.html" , param=param ,post= post)
    if request.method=="POST":
        username = request.form.get('email')
        password = request.form.get('password')
        if username == param['login_username'] and password == param['login_password']:
            session['user'] = username
            post = posts.query.all()
            return render_template("dashboard.html" , param=param , post = post)
    
    return render_template("login.html", param=param)



@app.route('/contact', methods = ['GET','POST'])
def contact():
    if request.method == 'POST':
        Name = request.form.get('name')
        Email = request.form.get('email')
        phone_number = request.form.get('ph')
        message = request.form.get('msg')
        entry = contacts(

            name=Name , email=Email ,
            phone_number = phone_number ,
            message = message , date = datetime.now())

        db.session.add(entry) 
        db.session.commit()
        mail.send_message(

            'New message from : '+ Name,sender = Email ,
             recipients = [param["recipients"]],
              body = message +'\nphone number : ' + phone_number )


    return render_template('contact.html', param=param)
@app.route('/about')
def about():
    return render_template('about.html',param=param)




@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', param=param , post = post)



@app.route('/edit/<string:sno>', methods = ['GET','POST'])
def edit(sno):
    if 'user' in session and session['user'] == param['login_username']:
        if request.method == 'POST':
            Title = request.form.get('title')
            Slug = request.form.get('slug')
            Image = request.form.get('image')
            Content = request.form.get('content')
            if sno == '0':
                adding_posts = posts(

                    title=Title , slug=Slug ,
                    img = Image ,
                    content = Content , date = datetime.now())

                db.session.add(adding_posts) 
                db.session.commit()
            else:
                post = posts.query.filter_by(sno=sno).first()
                post.title = Title,
                post.slug = Slug,
                post.img = Image,
                post.content = Content,
                post.date = datetime.now()
                db.session.commit()
                
                adding_posts = posts(

                    title=Title , slug=Slug ,
                    img = Image ,
                    content = Content , date = datetime.now())

                # db.session.add(adding_posts) 
                db.session.commit()
                return redirect('/edit/'+sno)
        post = posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', param=param, post=post)


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>" , methods=['GET', 'POST'])
def delete(sno):
    if "user" in session and session['user']==param['login_username']:
        post = posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")

app.run(debug = True)

