import os
import secrets
from PIL import Image
from flask_login import login_user, current_user, logout_user, login_required
from flask_login import LoginManager , UserMixin
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo , ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, url_for
from flask import render_template, request,redirect,flash
from test import test1
from summarizer import PreprocessDocs
from gensim.summarization.summarizer import summarize
import re
import gensim
import sys
# text rank extractive summary
from gensim.summarization.summarizer import summarize
from WC import wordcloud_custom
#from senti import
import spacy
import os
from spacytextblob.spacytextblob import SpacyTextBlob

app = Flask(__name__)


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
app.app_context().push()
bcrypt = Bcrypt(app)
picFolder = os.path.join('static', 'pics')
print(picFolder)
app.config['UPLOAD_FOLDER'] = picFolder
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


@app.route('/')
@app.route('/home')
def home():
    return render_template("landingpage.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
@app.route('/mentalhealth')
def mentalhealth():
    return render_template("mentalhealth.html")

@app.route('/test')
@login_required
def test():
    return render_template("index.html")


@app.route('/my_form_post', methods=['POST'])
def my_form_post():
    text = request.form['story']

    firstname = request.form['validationCustom01']
    lastname = request.form['validationCustom02']
    email = request.form['email']
    # profession = request.form['radio-stacked']

    worryReason = request.form['worry-reason']
    familySickness = request.form['familySickness']
    eatingHabit = request.form['eating-habit']
    anxiety = request.form['anxiousness']
    hobby = request.form['hobby']
    trauma = request.form['trauma']
    q1 = request.form['q1']
    q2 = request.form['q2']
    q3 = request.form['q3']
    q4 = request.form['q4']
    q5 = request.form['q5']
    q6 = request.form['q6']

    sentiment = ""
    # processed_text = text.upper()
    nlp = spacy.load('en_core_web_lg')
    nlp.add_pipe('spacytextblob')

    doc = nlp(text)
    # print (text)
    # Polarity: -0.125

    if doc._.polarity >= 0.15:
        sentiment = "Patient's mental health is fine"
    elif doc._.polarity <= -0.2:
        sentiment = "The patient will have to visit in person and get treated"
    else:
        sentiment = "Patient needs treatment"

     #WordCloud Block
    cloud = wordcloud_custom(text)

    # Summary Block
    preprocess = PreprocessDocs
    text1 = preprocess.read_text(text)
    result = summarize(".\n".join(text1))
    s = re.sub('\.+', '.', result)
    print("_______________________________________________________________")
    print(s)
    print("___________________________________________________________________")

    if request.method == 'POST':
        t1 = request.form.get('sad')
        t2 = request.form.get('future')
        t3 = request.form.get('failure')
        t4 = request.form.get('enjoythings')
        t5 = request.form.get('guilt')
        t6 = request.form.get('punishment')
        t7 = request.form.get('selfloathing')
        t8 = request.form.get('selfblame')
        t9 = request.form.get('suicide')
        t10 = request.form.get('grieve')
        t11 = request.form.get('irritation')
        t12 = request.form.get('socialize')
        t13 = request.form.get('decisions')
        t14 = request.form.get('appearance')
        t15 = request.form.get('work')
        t16 = request.form.get('sleep')
        t17 = request.form.get('tiredness')
        t18 = request.form.get('appetite')
        t19 = request.form.get('weight')
        t20 = request.form.get('health')
        t = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16, t17, t18, t19, t20]
    else:
        t = ['NULL VALUE']


    print(t)
    ttest= test1(t)
    if request.form['action'] == 'Submit':
        return render_template("srt-resume.html", lname=lastname, fname=firstname, mail=email, reason=worryReason,fam=familySickness, eat=eatingHabit, anx=anxiety, hob=hobby, tra=trauma, senti=sentiment, smry=s, a1=q1, a2=q2, a3=q3, a4=q4, a5=q5, a6=q6)
    elif request.form['action'] == 'Submit1':
        return render_template("srt-resume.html", lname=lastname, fname=firstname, mail=email, reason=worryReason, fam=familySickness, eat=eatingHabit, anx=anxiety, hob=hobby, tra=trauma,senti= sentiment, smry=s, a1=q1, a2=q2, a3=q3, a4=q4, a5=q5, a6=q6)


if __name__ == '__main__':
    app.run(debug=True, port=3000)
