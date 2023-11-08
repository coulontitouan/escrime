from .app import app
from flask import render_template, redirect, url_for
from flask_login import login_user , current_user, logout_user
from flask import request
from flask_login import login_required
from wtforms import StringField , HiddenField
from wtforms.validators import DataRequired
from wtforms import PasswordField
from flask_wtf import FlaskForm
from hashlib import sha256



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
    username=StringField('Username')
    password=PasswordField("Password")
    next=HiddenField()
    
    def get_authenticated_user(self):
        return None
        if user is None:
            return None
        m=sha256()
        m.update(self.password.data.encode())
        passwd= m.hexdigest()
        return user if passwd == user.password else None

@app.route("/connexion/")
def connexion():
    return render_template(
        "connexion.html"
    )

@app.route("/deconnexion/")
def deconnexion():
    logout_user()
    return redirect(url_for("home"))