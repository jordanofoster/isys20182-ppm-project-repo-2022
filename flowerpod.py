import os, shutil
from dotenv import load_dotenv
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin, login_user, LoginManager, login_required, logout_user, current_user
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

#Loading our .env file
load_dotenv()

# Werkzeug vars
UPLOAD_FOLDER = os.getenv('WERKZEUG_UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

#Constructor
app = Flask(__name__)

#Setting up static folder for images, css etc.
app.static_folder = os.getenv('FLASK_STATIC_FOLDER')

bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_BINDS'] = { 'Guides' : 'sqlite:///guides.db', 'GuideImages' : 'sqlite:///guide-images.db'}
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please login to continue."

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

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def in_accessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

admin = Admin(app)
admin.add_view(MyModelView(GuideImages, db.session))
admin.add_view(MyModelView(Guides, db.session))

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
    next = HiddenField()
    submit = SubmitField("Login")

class SearchForm(FlaskForm):
    search = StringField("Search", validators=[InputRequired()])
    submit = SubmitField("Search")

class NewGuideForm(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(min=5, max=50)])
    creator = StringField(validators=[InputRequired(), Length(min=5, max=30)])
    images = MultipleFileField(validators=[FileRequired()])
    submit = SubmitField("Create")

#Form for each individual caption input
class caption(Form):
    caption = StringField(validators=[InputRequired()])

#Form for captionForm passed to new-guide-content 
class CaptionForm(FlaskForm):

    captionList = FieldList(FormField(caption))
    submit = SubmitField("Create")

class imageCaptionPair(Form):
    image = FileField()
    caption = StringField()

class editGuideForm(FlaskForm):
    title = StringField(validators=[Length(min=5, max=50)])
    creator = StringField(validators=[Length(min=5, max=30)])
    listPair = FieldList(FormField(imageCaptionPair))
    submit = SubmitField("Submit Changes")

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
    
    return render_template('main-page.html', form=form, htmlTitle="Main Page")

@app.route("/login", methods=['GET', 'POST'])
def login():
    #calls form for inputboxes and button
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        next_url = request.form.get('next')
        if user:
            
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('home'))
            
    return render_template('login.html', form=form, htmlTitle="Login")

def getGuides(databaseGuides):
    data, temp = [],[]

    for guide in databaseGuides:
        temp.append(guide.id)
        temp.append(guide.title)
        temp.append(guide.creator)
        temp.append(GuideImages.query.filter_by(guideID=guide.id).all())

        data.append(temp.copy())
        temp.clear()

    return data

@app.route("/home", methods=['GET', 'POST'])
def home():

    form = SearchForm()
    guides = Guides.query.all()

    data = getGuides(guides)

    if form.validate_on_submit():
        guide.search = form.search.data
        guides = guides.filter(Guides.title.like('%' + guide.search + '%'))
        guides = guides.order_by(Guides.title).all()
        data = getGuides(guides)

        return render_template("search.html", 
                                form=form, 
                                data=data, 
                                search=guide.search, 
                                htmlTitle="Search")

    return render_template('home.html',
                            form=form,
                            data=data, 
                            htmlTitle="Home")

@app.route('/search', methods=["POST"])
def search():

    form = SearchForm()
    guides = Guides.query

    guide.search = form.search.data
    guides = guides.filter(Guides.title.like('%' + guide.search + '%'))
    guides = guides.order_by(Guides.title).all()
    data = getGuides(guides)

    return render_template("search.html",
                            form=form,
                            data=data,
                            search=guide.search, 
                            guides=guides, 
                            htmlTitle="Search")


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
        

@app.route("/new-guide", methods=['GET', 'POST'])
@login_required
def newGuide():
    form = NewGuideForm()

    if request.method == 'POST':

        pathString = f'{app.root_path}{UPLOAD_FOLDER}/{form.title.data.replace(" ", "_")}'

        try:
            os.makedirs(pathString)

            new_guide = Guides(title=form.title.data, creator=str(current_user.username))
            db.session.add(new_guide)
            db.session.commit()

            for i, image in enumerate(form.images.data):

                #ISSUE: 
                #SELECT ORDER OF IMAGES IN FORM DOES NOT AFFECT ORDER IN FLASK.
                #UPLOAD ORDER IS BASED ON FILEEXPLORER SORT METHOD.
                #No workarounds found.

                ext = image.filename.rfind(".")
                image_ext = image.filename[ext:]

                image_filename = f'{i+1}{image_ext}'

                image.save(os.path.join(pathString, image_filename))
                imageURI = f'{pathString}/{image_filename}'

                #REMOVE WHOLE PATH-ONLY UP TO STATIC/../../../imagename.filetype
                index = imageURI.find("static/")
                imageURI = imageURI[index-1:]

                new_image = GuideImages(guideID=new_guide.id, image=imageURI, caption="null")
                db.session.add(new_image)
                db.session.commit()

            print(f"Num files: {len(request.files.getlist(form.images.name))}")

            #Return home when finished....
            return redirect(url_for('newGuideContent', guide_id=new_guide.id))
        except:
            pass
            
    return render_template('new-guide.html', form=form, htmlTitle="New Guide")

@app.route(f"/new-guide-content/<int:guide_id>", methods=['GET', 'POST'])
@login_required
def newGuideContent(guide_id):

    guide = Guides.query.filter_by(id=guide_id).one()
    guideContent = GuideImages.query.filter_by(guideID=guide_id).all()
    form = CaptionForm()

    if request.method == 'GET':

        for i in range(len(guideContent)):
            form.captionList.append_entry()

        for(guide, entry) in zip(guideContent, form.captionList.entries):
            entry.label = "../" + guide.image

    if request.method == 'POST':

        for(guide, entry) in zip(guideContent, form.captionList.entries):
            newCaption = entry.data
            newCaption = newCaption.get('caption')
            guide.caption = newCaption
            db.session.commit()

        return redirect(url_for('home'))

    

    return render_template('new-guide-content.html', form=form, guides=guideContent, htmlTitle="New Guide")


@app.route("/guide/<int:guide_id>/delete", methods=['GET', 'POST'])
@login_required
def deleteGuide(guide_id):
    toDelGuide = Guides.query.filter_by(id=guide_id).one()
    toDelImages = GuideImages.query.filter_by(guideID=guide_id).all()

    title = toDelGuide.title
    title = title.replace(" ", "_")
    path = f"{app.root_path}/{UPLOAD_FOLDER[1:]}/{title}"
    print("\nTrying to delete guide...")
    try:
        shutil.rmtree(path)
        print(f"Deleted guides folder and folder content at {path}")
        db.session.delete(toDelGuide)
        for image in toDelImages:
            db.session.delete(image)
        db.session.commit()
        flash("Guide deleted.")
        print(f"Removed from guides.db --> {toDelGuide.title} (ID:{toDelGuide.id})\n")

    except:
        print("Error deleting path")
        db.session.delete(toDelGuide)
        for image in toDelImages:
            db.session.delete(image)
        db.session.commit()
        print(f"Removed from guides.db --> {toDelGuide.title} (ID:{toDelGuide.id})\n")

    return redirect(url_for('home'))

@app.route("/guide/<int:guide_id>/edit", methods=['GET', 'POST'])
@login_required
def editGuide(guide_id):

    guide = Guides.query.filter_by(id=guide_id).one()
    images = GuideImages.query.filter_by(guideID=guide_id).all()
    form = editGuideForm()
    
    if request.method == 'GET':
        form.title.data = guide.title
        form.creator.data = guide.creator

        for i in range(len(images)):
            form.listPair.append_entry()

        for(image, entry) in zip(images, form.listPair.entries):
            entry.label = "../" + image.image

    if request.method == 'POST':

        if form.title.data != guide.title:

            #CHANGING ALL PATHS RELATED TO A NEW GUIDE TITLE

            ogPath = f'{app.root_path}{UPLOAD_FOLDER}/{guide.title.replace(" ", "_")}'

            #Update the guide title in DB
            guide.title = form.title.data
            db.session.commit()

            newPath = f'{app.root_path}{UPLOAD_FOLDER}/{form.title.data.replace(" ", "_")}'

            os.rename(ogPath, newPath)


            #Changing each image path to fit the new path
            for image in images:
                x = image.image.rfind("/")
                imageName = image.image[x+1:]
                
                image.image = f'{UPLOAD_FOLDER}/{form.title.data.replace(" ", "_")}/{imageName}'
                
            db.session.commit()

        for i, (guideImage, entry) in enumerate(zip(images, form.listPair.entries)):
            
            entryData = entry.data
            newImage = entryData.get('image')

            newCaption = entryData.get('caption')

            if str(newImage) == "<FileStorage: '' ('application/octet-stream')>":
                #FileField is left blank...
                pass
            else:
                #FileField is not blank
                #Index for newImage .filetype
                x = newImage.filename.rfind(".")

                try:
                    os.remove(f'{app.root_path}{guideImage.image}')
                except:
                    pass
                
                imgName = f"{i+1}{newImage.filename[x:]}"


                try:
                    newImage.save(f'{app.root_path}/{UPLOAD_FOLDER}/{form.title.data.replace(" ", "_")}/{imgName}')
                except:
                    os.mkdir(f'{app.root_path}/{UPLOAD_FOLDER}/{form.title.data.replace(" ", "_")}')
                    newImage.save(f'{app.root_path}/{UPLOAD_FOLDER}/{form.title.data.replace(" ", "_")}/{imgName}')

                
                newImage = f'{UPLOAD_FOLDER}/{form.title.data.replace(" ", "_")}/{imgName}'
                guideImage.image = newImage
                db.session.commit()

            guideImage.caption = newCaption
            db.session.commit()
            flash("Changes saved successfully.")

        return redirect(url_for('home'))

    return render_template('edit.html', form=form, guide=guide, images=images, htmlTitle="Edit Guide")

@app.route("/guide/<int:guide_id>")
def guide(guide_id):
    
    guide = Guides.query.filter_by(id=guide_id).one()
    images = GuideImages.query.filter_by(guideID=guide_id).all()
    return render_template('guide.html', guide=guide, images=images, htmlTitle=f"Guide {guide_id}")



@app.route("/logout", methods=['GET', 'POST'])
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
    
    return render_template('register.html', form=form, htmlTitle="Register")

if __name__ == "__main__":
    app.run()

