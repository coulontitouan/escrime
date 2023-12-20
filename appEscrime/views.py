from .app import app ,db
from flask import flash, render_template, redirect, url_for, request
from flask_login import login_user , current_user, logout_user, login_required
from wtforms import StringField , HiddenField, DateField , RadioField, PasswordField,SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from hashlib import sha256
from .models import *
from .commands import newuser

with app.app_context():
    class CreeCompetitionForm(FlaskForm):
        """Classe qui permet de créer une compétition"""
        nom_lieu = StringField('Nom lieu',validators=[DataRequired()])
        adresse_lieu = StringField('Adresse lieu',validators=[DataRequired()])
        ville_lieu = StringField('Ville lieu',validators=[DataRequired()])
        nom_competition = StringField('Nom compétition',validators=[DataRequired()])
        date_competition = DateField('Date compétition', format='%Y-%m-%d', validators=[DataRequired()])
        sexe_competition = RadioField('Sexe',choices = ['Hommes','Femmes'])
        coefficient_competition = StringField('Coefficient',validators=[DataRequired()])
        nom_arme = SelectField("Arme",coerce=str,default=1)
        nom_categorie = SelectField("Catégorie",coerce=str,default=1)
        next = HiddenField()
    
@app.route("/")
def home():
    competitions = get_all_competitions()
    return render_template(
        "home.html",
        competitions = competitions
    )

@app.route("/informations")
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
    prenom = StringField('prenom',validators=[DataRequired()])
    nom = StringField('nom',validators=[DataRequired()])
    sexe = RadioField('sexe',choices = ['Homme','Femme'],validators=[DataRequired()])
    date_naissance = DateField('date',validators=[DataRequired()])
    club = SelectField("club",coerce=str,default=2,validators=[DataRequired()], choices = [(1,""),(2,""),(3,""),(4,""),(5,"")])
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
                return True
            else:
                return False
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
    selection_club.sort(key=lambda x: x[1])
    f2.club.choices = selection_club

    if not f.is_submitted():
        f.next.data = request.args.get("next")

    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            prochaine_page = f.next.data or url_for("home")
            back = request.referrer
            return redirect(prochaine_page)
    return render_template(
        "connexion.html",formlogin=f, formsignup = f2)

@app.route("/connexion/inscription", methods=("GET", "POST"))
def inscription():
    f =LoginForm()
    f2 = SignUpForm()
    selection_club = []
    for club in db.session.query(Club).all():
        if club.id !=1:
            selection_club.append((club.id,club.nom))
    f2.club.choices = selection_club
    if not f2.is_submitted():
        f2.next.data = request.args.get("next")
    elif f2.validate_on_submit():
        if f2.est_deja_inscrit_sans_mdp():
            user = f2.get_authenticated_user()
            if user:
                    login_user(user)
                    prochaine_page = f2.next.data or url_for("home")
                    return redirect(prochaine_page)
        elif f2.est_deja_inscrit_sans_mdp() == None:
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
    """Fonction qui permet d'afficher une compétition"""
    form = InscriptionForm()
    competition = get_competition(id)
    try :
        user = current_user.num_licence
    except :
        user = -1
    return render_template(
        "competition.html",
        competition = competition, form = form, user = competition.est_inscrit(user)
    )

@app.route("/competition/<int:id>/createPoule")
def competitionCreatePoules(id):
    """Fonction qui permet de répartir les poules d'une compétition et redirige sur la page de cette compétition"""
    competition = get_competition(id)
    competition.programme_poules()
    return redirect(url_for("competition", id=id))

@app.route("/competition/<int:idC>/poule/<int:idP>")
def poule(idC, idP):
    """Fonction qui permet d'afficher une poule"""
    return render_template(
        "poule.html"
    )

@app.route("/deconnexion/")
def deconnexion():
    logout_user()
    return redirect(url_for("home"))

@app.route('/cree/competition', methods=("GET", "POST"))
@login_required
def creationCompet():
    """Fonction qui permet de créer une compétition"""
    f = CreeCompetitionForm()
    f.nom_arme.choices = cree_liste(get_all_armes())
    f.nom_categorie.choices = cree_liste(get_all_categories())
    if current_user.is_admin() == False:
        return redirect(url_for("home"))
    if not  f.is_submitted():
        f.next.data = request.args.get("next")
    else:
        lieu = get_lieu(f.nom_lieu.data, f.adresse_lieu.data, f.ville_lieu.data)
        arme = get_arme(f.nom_arme.data)
        categorie = get_categorie(f.nom_categorie.data)
        if lieu is None:
            lieu = Lieu(nom =  f.nom_lieu.data, adresse =  f.adresse_lieu.data, ville =  f.ville_lieu.data)
            db.session.add(lieu)
            db.session.commit()
        sexe = f.sexe_competition.data
        if sexe == "Femmes":
            sexe = "Dames"
        if sexe == "Hommes":
            sexe = "Homme"
        competition = Competition(id = (get_max_competition_id() + 1), nom = f.nom_competition.data, date = f.date_competition.data, coefficient = f.coefficient_competition.data, sexe = sexe, id_lieu = lieu.id, id_arme = arme.id, id_categorie = categorie.id)
        db.session.add(competition)
        db.session.commit()
        flash('Compétition créée avec succès', 'success')  # Utilise Flash de Flask pour les messages
        return redirect(url_for('home'))
    return render_template('cree-competition.html', form=f)

@app.route("/profil")
def profil():
    return render_template(
        "profil.html"
    )

class Changer_mdpForm(FlaskForm):
    new_mdp=PasswordField("Password",validators=[DataRequired()])
    next = HiddenField()

@app.route("/profil/changer-mdp", methods=("POST",))
def changer_mdp() :
    f = Changer_mdpForm()
    return render_template("changer-mdp.html", f = f)

from flask import request, jsonify
import os, signal
@app.route("/shutdown", methods=['GET'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({ "success": True, "message": "Server is shutting down..." })

class InscriptionForm(FlaskForm):
        role = RadioField('Role',choices = ['Arbitre','Tireur'])
        next = HiddenField()

@app.route("/competition/<int:id>/inscription", methods=("GET", "POST"))
def inscription_competition(id) :
    """Inscrit un utilisateur à une compétition spécifique.

    Args:
        id (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page de la compétition
    """
    form = InscriptionForm()
    competition = get_competition(id)
    inscrit = competition.est_inscrit(current_user.num_licence)
    if not form.is_submitted() :
        form.next.data = request.args.get("next")
    else :
        if form.role.data == "Arbitre" and not inscrit :
            competition.inscription(current_user.num_licence,True)
            flash('Vous êtes inscrit comme arbitre', 'success')
            return redirect(url_for('competition',id = id))
        if form.role.data == "Tireur" and not inscrit :
            competition.inscription(current_user.num_licence)
            flash('Vous êtes inscrit comme tireur', 'success')
            return redirect(url_for('competition', id = id))
        flash('Vous êtes déja inscrit', 'danger')
        return redirect(url_for('competition', id = id))
    return render_template('competition.html',form = form, competition = competition, id = id)

@app.route("/home/suppr-competition/<int:id>")
def suppr_competition(id : int) :
    """Supprime une compétition.

    Args:
        id (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page d'accueil
    """
    delete_competition(id)
    flash('Compétition supprimée avec succès', 'warning')

    return redirect(url_for('home'))

@app.route("/competition/<int:id>/deinscription", methods=("GET", "POST"))
def deinscription_competition(id : int) :
    """Gère la désinscription d'un utilisateur à une compétition spécifique.

    Args:
        id (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page de la compétition
    """
    form = InscriptionForm()
    competition = get_competition(id)
    competition.desinscription(current_user.num_licence)
    flash('Vous êtes désinscrit', 'warning')

    return render_template('competition.html', form=form, competition=competition, id=id)

