import os
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from sqlalchemy import null
from wtforms import StringField, PasswordField, MultipleFileField, FileField, SubmitField, FieldList, FormField, Form, HiddenField
from wtforms.validators import InputRequired, DataRequired, Length, ValidationError
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
app.config['SQLALCHEMY_BINDS'] = {'Guides' : 'sqlite:///guides.db',
                                    'GuideImages' : 'sqlite:///guide-images.db'}
app.config['SECRET_KEY'] = '\xef;\x96=\x11DE\xe2S\x91\x8a2'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Guides(db.Model):
    __bind_key__ = 'Guides'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    creator = db.Column(db.String(20), nullable=False)

class GuideImages(db.Model):
    __bind_key__ = 'GuideImages'
    id = db.Column(db.Integer, primary_key=True)
    guideID = db.Column(db.Integer)
    image = db.Column(db.String)
    caption = db.Column(db.String, nullable=True)

lists = ["Content Title 1", "Content Title 2"]
list2 = ["NAME YTUh", "duee vaee2"]

for one, two in lists, list2:
    print(one + two)

