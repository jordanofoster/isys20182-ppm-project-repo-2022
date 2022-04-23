import os
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, FileField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import flask_wtf
import wtforms
from flask_bcrypt import Bcrypt
from tts import text_to_speech
from werkzeug.utils import secure_filename

# Werkzeug vars
UPLOAD_FOLDER = '/static/guides/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#Constructor
app = Flask(__name__)

#Setting up static folder for images, css etc.
app.static_folder = 'static'

bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_BINDS'] = {'Posts' : 'sqlite:///posts.db'}
app.config['SECRET_KEY'] = '\xef;\x96=\x11DE\xe2S\x91\x8a2'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Setting up Database table
#If DB file is not setup, do as follows:
#from flowerpod import db
#db.create_all()
#SQLite3 can verify creation of table.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Posts(db.Model):
    __bind_key__ = 'Posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    creator = db.Column(db.String(20))
    image = db.Column(db.String)
    content = db.Column(db.String)

#Creating databases
db.create_all()

#Register form where username/password are inputboxes and submit is a button.
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()

        if existing_user_username:
            raise ValidationError("Username taken")

#Login form where username/password are inputboxes and submit is a button.
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Login")

class NewGuideForm(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(min=5, max=50)])
    creator = StringField(validators=[InputRequired(), Length(min=5, max=30)])
    image = FileField(validators=[FileRequired()])
    content = StringField(validators=[InputRequired(), Length(min=5)])
    submit = SubmitField("Create")

class MainPageForm(FlaskForm):
    submit = SubmitField("")
    
#Default URL returns mainpage.html
@app.route("/", methods=['GET', 'POST'])
@cross_origin()
def mainPage():
    form = MainPageForm()
    
    if request.method == 'POST':
        text = "Welcome to the FlowerPod Website."
        text += " Here you can find gardening guides, tips and tricks!"
        text += " Make an account or sign in to get started."
        text_to_speech(text, "Male")
        
        return render_template('mainPage.html', form=form)
    
    return render_template('mainPage.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    #calls form for inputboxes and button
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user:
            
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            
    return render_template('login.html', form=form)


@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    posts = Posts.query.all()

    return render_template('home.html', posts=posts)

def allowed_file(filename):
    return "." in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
        
@app.route("/new-guide", methods=['GET', 'POST'])
@login_required
def newGuide():
    form = NewGuideForm()

    if request.method == 'POST':
        image_data = form.image.data
        image_filename = secure_filename(image_data.filename)
        image_data.save(os.path.join(app.root_path, 'static/guides/images/', image_filename))
        imageURI = f'/static/guides/images/{image_filename}'

        new_post = Posts(title=form.title.data, creator=form.creator.data, image=imageURI, content = form.content.data)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('home'))
            
    return render_template('newGuide.html', form=form)

@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Posts.query.filter_by(id=post_id).one()
    
    return render_template('post.html', post=post)

@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('mainPage'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    #calls form for inputboxes and button
    form = RegisterForm()

    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run()

