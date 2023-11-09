from .app import app ,db
from flask import render_template, redirect, url_for, session
from flask_login import login_user , current_user, logout_user
from flask import request,redirect, url_for
from flask_login import login_required
from wtforms import StringField , HiddenField, DateField , RadioField, PasswordField,SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from hashlib import sha256
from .models import *
from .commands import newuser,updateuser
from wtforms import DateField

class CreeCompetitionForm(FlaskForm):
    nom_lieu = StringField('Nom lieu',validators=[DataRequired()])
    addresse_lieu = StringField('Addresse lieu',validators=[DataRequired()])
    nom_competition = StringField('Nom compétition',validators=[DataRequired()])
    date_competition = DateField('Date compétition', format='%Y-%m-%d', validators=[DataRequired()])
    coefficient_competition = StringField('Coefficient',validators=[DataRequired()])
    nom_arme = StringField('Nom arme',validators=[DataRequired()])
    nom_categorie = StringField('Nom catégorie',validators=[DataRequired()])
    next = HiddenField()
    
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
    sexe = RadioField('sexe',choices = ['Homme','Femme'])
    date_naissance = DateField('date')
    club = SelectField("club",coerce=str,default=2, choices = [(1,""),(2,""),(3,""),(4,""),(5,"")])
    next=HiddenField()

    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        m=sha256()
        m.update(self.mot_de_passe.data.encode())
        passwd= m.hexdigest()
        return user if passwd == user.mot_de_passe else None
    
    
    def est_deja_inscrit_sans_mdp(self):
        user = Escrimeur.query.get(self.num_licence.data)
        a= "Homme"
        if user is not None:
            if self.sexe.data == "Femme":
                a = "Dames" 
            if user.sexe == a and user.prenom.upper() == self.prenom.data.upper() and user.nom.upper() == self.nom.data.upper():
                m=sha256()
                m.update(self.mot_de_passe.data.encode())
                passwd= m.hexdigest()
                user.set_mdp(passwd)
                db.session.commit()
        else:
            return None

@app.route("/connexion/", methods=("GET", "POST"))
def connexion():
    f =LoginForm()
    f2 = SignUpForm()
    selection_club = []
    for club in db.session.query(Club).all():
        if club.id != 1:
            selection_club.append((club.id, club.nom))
    f2.club.choices = selection_club
    if not f.is_submitted():
        f.next.data = request.args.get("next")

    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            prochaine_page = f.next.data or url_for("home")
            return redirect(prochaine_page)
    return render_template(
        "connexion.html",formlogin=f, formsignup = f2)

@app.route("/connexion/inscription", methods=("GET", "POST"))
def inscription():
    f =LoginForm()
    f2 = SignUpForm()
    if not f2.is_submitted():

        f2.next.data = request.args.get("next")
    elif f2.validate_on_submit():
        f2.est_deja_inscrit_sans_mdp()
        user = f2.get_authenticated_user()
        if user:
                login_user(user)
                prochaine_page = f2.next.data or url_for("home")
                return redirect(prochaine_page)
    else:
        if f2.sexe.data == "Femme":
            newuser(f2.num_licence.data,f2.mot_de_passe.data,f2.prenom.data,f2.nom.data,"Dames",f2.date_naissance.data,f2.club.data)
        else:       
            newuser(f2.num_licence.data,f2.mot_de_passe.data,f2.prenom.data,f2.nom.data,"Homme",f2.date_naissance.data,f2.club.data)

            user = f2.get_authenticated_user()
            if user:
                    login_user(user)
                    prochaine_page = f2.next.data or url_for("home")
                    return redirect(prochaine_page)

    return render_template(
        "connexion.html",formlogin=f, formsignup = f2)

@app.route("/competition/<int:id>")
def competition(id):
    return render_template(
        "competition.html"
    )

@app.route("/competition/<int:idC>/poule/<int:idP>")
def poule(idC, idP):
    return render_template(
        "poule.html"
    )
  
@app.route("/deconnexion/")
def deconnexion():
    logout_user()
    return redirect(url_for("home"))


@app.route('/Cree/Competition', methods=("GET", "POST"))
def creationCompet():
    f = CreeCompetitionForm()
    if not  f.is_submitted():
        f.next.data = request.args.get("next")
    else:
        lieu = get_lieu(f.addresse_lieu.data)
        arme = get_arme(f.nom_arme.data)
        categorie = get_categorie(f.nom_categorie.data)
        if lieu is None:
            lieu = Lieu(nom =  f.nom_lieu.data,adresse =  f.addresse_lieu.data)
            db.session.add(lieu)
            db.session.commit()
        competition = Competition(id = (get_max_competition_id() + 1), nom = f.nom_competition.data, date = f.date_competition.data, coefficient = f.coefficient_competition.data, id_lieu = lieu.id, id_arme = arme.id, id_categorie = categorie.id)
        db.session.add(competition)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('cree-competition.html', form=f)

@app.route("/profil")
def profil():
    return render_template(
        "profil.html"
    )

# class Changer_mdpForm(FlaskForm):
#     new_mdp=PasswordField("Password",validators=[DataRequired()])
#     next = HiddenField()

# @app.route("/profil/changer-mdp", methods=("POST",))
# def changer_mdp():
#     f =Changer_mdpForm()
#     return render_template(
#         "changer-mdp.html", f
#     )


