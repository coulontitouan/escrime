from .app import app
from flask import render_template
from flask_login import login_user , current_user, logout_user
from flask import request
from flask_login import login_required
from wtforms import StringField , HiddenField
from wtforms.validators import DataRequired
from wtforms import PasswordField
from wtforms import RadioField
from flask_wtf import FlaskForm
from hashlib import sha256
from .models import Escrimeur



@app.route("/")
def home():
    return render_template(
        "home.html"
    )

@app.route("/informations/")
def informations():
    return render_template(
        "informations.html"
    )


class LoginForm(FlaskForm):
    num_licence=StringField('num_licence',validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    next = HiddenField()
    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        m=sha256()
        m.update(self.password.data.encode())
        passwd= m.hexdigest()
        return user if passwd == user.password else None
    
class SignUpForm(FlaskForm):
    num_licence=StringField('num_licence',validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    prenom = StringField('prenom')
    nom = StringField('nom')
    sexe = RadioField('sexe',choices = ['homme','femme'])
    next=HiddenField()

    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        m=sha256()
        m.update(self.password.data.encode())
        passwd= m.hexdigest()
        return user if passwd == user.password else None
    

@app.route("/connexion/")
def connexion():
    f =LoginForm()
    f2 = SignUpForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for("home")
            return redirect(next)
        
    if not f2.is_submitted():
        f2.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f2.get_authenticated_user()
        if user:
            login_user(user)
            next = f2.next.data or url_for("home")
            return redirect(next)
    return render_template(
        "connexion.html",formlogin=f, formsignup = f2)

