"""Module qui contient les fonctions qui permettent de gérer les routes de l'application"""

import os
import signal
from flask import request, redirect, url_for, flash, render_template, jsonify
from flask_login import login_user , current_user, logout_user, login_required
from wtforms import StringField , HiddenField, DateField , RadioField, PasswordField,SelectField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
import appEscrime.constants as cst
from .app import app ,db
from .models import Escrimeur, Club, Competition, Lieu
from . import requests as rq
from .commands import newuser
from .requests import get_tireur

with app.app_context():
    class CreeCompetitionForm(FlaskForm):
        """Classe qui permet de créer une compétition"""
        nom_lieu = StringField('Nom lieu', validators=[DataRequired()])
        adresse_lieu = StringField('Adresse lieu', validators=[DataRequired()])
        ville_lieu = StringField('Ville lieu', validators=[DataRequired()])
        nom_competition = StringField('Nom compétition', validators=[DataRequired()])
        date_competition = DateField('Date compétition',
                                     format='%Y-%m-%d', validators=[DataRequired()])
        sexe_competition = RadioField('Sexe', choices = ['Hommes','Femmes'])
        coefficient_competition = StringField('Coefficient', validators=[DataRequired()])
        nom_arme = SelectField("Arme", coerce=str, default=1)
        nom_categorie = SelectField("Catégorie", coerce=str, default=1)
        next = HiddenField()

@app.route("/")
def home():
    competitions = rq.get_all_competitions()
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
    num_licence = StringField('num_licence', validators=[DataRequired()])
    mot_de_passe = PasswordField("Password", validators=[DataRequired()])
    next = HiddenField()

    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        cst.CRYPTAGE.update(self.mot_de_passe.data.encode())
        passwd = cst.CRYPTAGE.hexdigest()
        return user if passwd == user.mot_de_passe else None


class SignUpForm(FlaskForm):
    num_licence = StringField('num_licence', validators=[DataRequired()])
    mot_de_passe = PasswordField("Password", validators=[DataRequired()])
    prenom = StringField('prenom', validators=[DataRequired()])
    nom = StringField('nom', validators=[DataRequired()])
    sexe = RadioField('sexe', choices = ['Homme','Femme'],validators=[DataRequired()])
    date_naissance = DateField('date', validators=[DataRequired()])
    club = SelectField("club",
                       coerce=str,
                       default=2, validators=[DataRequired()],
                       choices = [(1,""),(2,""),(3,""),(4,""),(5,"")])
    next = HiddenField()

    def get_authenticated_user(self):
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        cst.CRYPTAGE.update(self.mot_de_passe.data.encode())
        passwd = cst.CRYPTAGE.hexdigest()
        return user if passwd == user.mot_de_passe else None

    def est_deja_inscrit_sans_mdp(self):
        user = Escrimeur.query.get(self.num_licence.data)
        sexe = "Homme"
        if user is not None:
            if self.sexe.data == "Femme":
                sexe = "Dames"
            check_sexe = user.sexe == sexe
            check_prenom = user.prenom.upper() == self.prenom.data.upper()
            check_nom = user.nom.upper() == self.nom.data.upper()
            if check_sexe and check_prenom and check_nom:
                cst.CRYPTAGE.update(self.mot_de_passe.data.encode())
                passwd= cst.CRYPTAGE.hexdigest()
                user.set_mdp(passwd)
                db.session.commit()
                return True
            return False
        return None

@app.route("/connexion/", methods=("GET", "POST"))
def connexion():
    form = LoginForm()
    form2 = SignUpForm()
    selection_club = []
    for club in db.session.query(Club).all():
        if club.id != cst.CLUB_ADMIN:
            selection_club.append((club.id, club.nom))
    selection_club.sort(key=lambda x: x[1])
    form2.club.choices = selection_club

    if not form.is_submitted():
        form.next.data = request.args.get("next")

    elif form.validate_on_submit():
        user = form.get_authenticated_user()
        if user:
            login_user(user)
            prochaine_page = form.next.data or url_for("home")
            return redirect(prochaine_page)
    return render_template(
        "connexion.html",formlogin=form, formsignup = form2
        )

@app.route("/connexion/inscription", methods=("GET", "POST"))
def inscription():
    form = LoginForm()
    form2 = SignUpForm()
    selection_club = []
    for club in db.session.query(Club).all():
        if club.id != 1:
            selection_club.append((club.id,club.nom))
    form2.club.choices = selection_club
    if not form2.is_submitted():
        form2.next.data = request.args.get("next")
    elif form2.validate_on_submit():
        if form2.est_deja_inscrit_sans_mdp():
            user = form2.get_authenticated_user()
            if user:
                login_user(user)
                prochaine_page = form2.next.data or url_for("home")
                return redirect(prochaine_page)
        elif form2.est_deja_inscrit_sans_mdp() is None:
            if form2.sexe.data == "Femme":
                sexe = "Dames"
            else:
                sexe = "Hommes"
            newuser(form2.num_licence.data,
                    form2.mot_de_passe.data,
                    form2.prenom.data,
                    form2.nom.data,
                    sexe,
                    form2.date_naissance.data,
                    form2.club.data)
            user = form2.get_authenticated_user()
            if user:
                login_user(user)
                prochaine_page = form2.next.data or url_for("home")
                return redirect(prochaine_page)
    return render_template("connexion.html",
                           formlogin = form,
                           formsignup = form2)

@app.route("/competition/<int:id_compet>")
def affiche_competition(id_compet):
    """Fonction qui permet d'afficher une compétition"""
    form = InscriptionForm()
    competition = rq.get_competition(id_compet)
    try :
        user = current_user.num_licence
    except AttributeError:
        user = -1
    return render_template(
        "competition.html",
        competition = competition, form = form, user = competition.est_inscrit(user),get_tireur=get_tireur,
    )

@app.route("/competition/<int:id_compet>/createPoule")
def competition_cree_poules(id_compet):
    """Fonction qui permet de répartir les poules d'une compétition et redirige sur la page de cette compétition"""
    competition = rq.get_competition(id_compet)
    competition.programme_poules()
    return redirect(url_for("competition", id=id_compet))

@app.route("/competition/<int:id_compet>/poule/<int:id_poule>")
def affiche_poule(id_compet, id_poule): # pylint: disable=unused-argument
    """Fonction qui permet d'afficher une poule"""
    return render_template(
        "poule.html"
    )

@app.route("/deconnexion/")
def deconnexion():
    """Déconnecte un utilisateur"""
    logout_user()
    return redirect(url_for("home"))

@app.route('/cree/competition', methods=("GET", "POST"))
@login_required
def creation_competition():
    """Fonction qui permet de créer une compétition"""
    form = CreeCompetitionForm()
    form.nom_arme.choices = rq.cree_liste_nom_objet(rq.get_all_armes())
    form.nom_categorie.choices = rq.cree_liste_nom_objet(rq.get_all_categories())
    if current_user.is_admin() is False:
        return redirect(url_for("home"))
    if not form.is_submitted():
        form.next.data = request.args.get("next")
    else:
        lieu = rq.get_lieu(form.nom_lieu.data, form.adresse_lieu.data, form.ville_lieu.data)
        arme = rq.get_arme(form.nom_arme.data)
        categorie = rq.get_categorie(form.nom_categorie.data)
        if lieu is None:
            lieu = Lieu(nom = form.nom_lieu.data,
                        adresse = form.adresse_lieu.data,
                        ville = form.ville_lieu.data)
            db.session.add(lieu)
            db.session.commit()
        sexe = form.sexe_competition.data
        if sexe == "Femmes":
            sexe = "Dames"
        competition = Competition(id=(rq.get_max_competition_id() + 1),
                                  nom=form.nom_competition.data,
                                  date=form.date_competition.data,
                                  coefficient=form.coefficient_competition.data,
                                  sexe=sexe,
                                  id_lieu=lieu.id,
                                  id_arme=arme.id,
                                  id_categorie=categorie.id)
        db.session.add(competition)
        db.session.commit()
        flash('Compétition créée avec succès', 'success') #Utilise Flash de Flask pour les messages
        return redirect(url_for('home'))
    return render_template('cree-competition.html', form=form)

@app.route("/profil")
def profil():
    return render_template(
        "profil.html"
    )

class ChangerMdpForm(FlaskForm):
    new_mdp = PasswordField("Password",validators=[DataRequired()])
    next = HiddenField()

@app.route("/profil/changer-mdp", methods=("POST",))
def changer_mdp():
    form =ChangerMdpForm()
    return render_template("changer-mdp.html", form=form)

@app.route("/shutdown", methods=['GET'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({"success": True, "message": "Server is shutting down..."})

class InscriptionForm(FlaskForm):
    role = RadioField('Role', choices = ['Arbitre','Tireur'])
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
    competition = rq.get_competition(id)
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

@app.route("/suppr-competition/<int:id_compet>")
def suppr_competition(id_compet : int) :
    """Supprime une compétition.

    Args:
        id_compet (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page d'accueil
    """
    rq.delete_competition(id_compet)
    flash('Compétition supprimée avec succès', 'warning')

    return redirect(url_for('home'))

class MatchForm(FlaskForm):
    touches1 = StringField('touches1',validators=[DataRequired()])
    touches2 = StringField('touches2',validators=[DataRequired()])
    next=HiddenField()

@app.route("/competition/<int:id_compet>/poule/<int:id_poule>/match/<int:id_match>")
def affiche_match(id_compet, id_poule, id_match):
    """Fonction qui permet d'afficher un match"""

    competition, poule, match = [None, None, None]
    # competition = get_competition(idC)
    # poule = get_poule(idC, idP)
    # match = get_match(idC, idP, idM)

    return render_template(
        "match.html",
        competition = competition, 
        poule = poule, 
        match = match
    )

@app.route("/competition/<int:id_compet>/deinscription", methods=("GET", "POST"))
def deinscription_competition(id_compet : int) :
    """Gère la désinscription d'un utilisateur à une compétition spécifique.

    Args:
        id (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page de la compétition
    """
    form = InscriptionForm()
    competition = rq.get_competition(id_compet)
    competition.desinscription(current_user.num_licence)
    flash('Vous êtes désinscrit', 'warning')
    return render_template('competition.html',
                           form=form,
                           competition=rq.get_competition(id_compet),
                           id=id_compet)
  
@app.errorhandler(Exception)
def page_not_found(erreur):
    """Fonction d'affichage de la page d'erreur."""
    return render_template('erreur.html', code=erreur.code, message=erreur.__class__.__name__), erreur.code
