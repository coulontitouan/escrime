from .app import app ,db
from flask import render_template, redirect, url_for
from flask_login import login_user , current_user, logout_user
from flask import request,redirect, url_for
from flask_login import login_required
from wtforms import StringField , HiddenField
from wtforms.validators import DataRequired
from wtforms import PasswordField
from wtforms import RadioField
from flask_wtf import FlaskForm
from hashlib import sha256
from .models import Escrimeur
from .commands import newuser,updateuser

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
    mot_de_passe=PasswordField("Password",validators=[DataRequired()])
    next = HiddenField()

    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        m=sha256()
        m.update(self.mot_de_passe.data.encode())
        passwd= m.hexdigest()
        return user if passwd == user.mot_de_passe else None
    
class SignUpForm(FlaskForm):
    num_licence=StringField('num_licence',validators=[DataRequired()])
    mot_de_passe=PasswordField("Password",validators=[DataRequired()])
    prenom = StringField('prenom')
    nom = StringField('nom')
    sexe = RadioField('sexe',choices = ['homme','femme'])
    next=HiddenField()

    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        m=sha256()
        m.update(self.mot_de_passe.data.encode())
        passwd= m.hexdigest()
        return user if passwd == user.mot_de_passe else None
    

@app.route("/connexion/", methods=("GET", "POST"))
def connexion():
    f =LoginForm()
    f2 = SignUpForm()
    print("Connexion")
    if not f.is_submitted():
        f.next.data = request.args.get("next")
        print("pas encore inscrit")

    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        print("num_licence = ",f.num_licence.data)
        print("password = ",f.mot_de_passe.data)
        if user:
            login_user(user)
            print("réussis")
            prochaine_page = f.next.data or url_for("home")
            return redirect(prochaine_page)

    return render_template(
        "connexion.html",formlogin=f, formsignup = f2)

@app.route("/connexion/inscription", methods=("GET", "POST"))
def inscription():
    f =LoginForm()
    f2 = SignUpForm()
    print("Inscription")
    if not f2.is_submitted():
        f2.next.data = request.args.get("next")
        print("pas encore inscrit")

    elif f2.validate_on_submit():
        print("num_licence = ",f2.num_licence.data)
        print("password  = ",f2.mot_de_passe.data)
        print("prenom  = ",f2.prenom.data)
        print("nom  = ",f2.nom.data)
        print("sexe  = ",f2.sexe.data)
        user = newuser(f2.num_licence.data,f2.mot_de_passe.data,f2.prenom.data,f2.nom.data,f2.sexe.data,)
        user = f2.get_authenticated_user()
        if user:
            login_user(user)
            print("réussis")
            prochaine_page = f2.next.data or url_for("home")
            return redirect(prochaine_page)

    return render_template(
        "connexion.html",formlogin=f, formsignup = f2)

@app.route("/competition/<int:id>")
def competition(id):
    return render_template(
        "competition.html"
    )

@app.route("/deconnexion/")
def deconnexion():
    logout_user()
    return redirect(url_for("home"))


