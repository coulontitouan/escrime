"""Module qui contient les fonctions qui permettent de gérer les routes de l'application"""

import os
import signal
from hashlib import sha256
from flask import abort, request, redirect, url_for, flash, render_template, jsonify
from flask_login import login_user , current_user, logout_user, login_required
from wtforms import StringField , HiddenField, DateField , RadioField, PasswordField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm
import appEscrime.constants as cst
from .app import app ,db
from .models import Escrimeur, Club, Competition, Lieu
from . import requests as rq
from .commands import newuser

with app.app_context() :
    class CreeCompetitionForm(FlaskForm) :
        """Classe formulaire pour la création d'une compétition.

        Args:
            FlaskForm (FlaskForm): Classe formulaire de Flask.
        """
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

class SearchForm(FlaskForm) :
    """Classe formulaire pour la recherche d'une compétition.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.
    """
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField("Submit", validators=[DataRequired()])

class HomeForm(FlaskForm) :
    """Classe formulaire pour le filtre de recherche d'une compétition.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.
    """
    categoriesField = SelectField("catégories",coerce=str,default=1, choices = ["Catégorie"])
    armesField = SelectField("armes",coerce=str,default=1, choices = ["Arme"])
    genresField = SelectField("genres",coerce=str,default=1, choices = ["Genre","Homme", "Dames"])

@app.route("/", methods =("GET","POST",))
def home() :
    """Fonction qui permet d'afficher la page d'accueil

    Returns:
        flask.Response: Renvoie la page d'accueil
    """
    form = HomeForm()
    for cat in rq.get_all_categories():
        form.categoriesField.choices.append(cat.libelle)
    for arme in rq.get_all_armes():
        form.armesField.choices.append(arme.libelle)
    competitions = Competition.query
    if form.categoriesField.data != "Catégorie" and form.categoriesField.data != "1":
        competitions = competitions.filter(
                        Competition.id_categorie == rq.get_categorie_par_libelle(form.categoriesField.data).id)
    if form.armesField.data != "Arme" and form.armesField.data != "1":
        competitions = competitions.filter(
                        Competition.id_arme == rq.get_arme_par_libelle(form.armesField.data).id)
    if form.genresField.data != "Genre" and form.genresField.data != "1":
        competitions = competitions.filter(
                        Competition.sexe == form.genresField.data)
    return render_template(
        "home.html",
        form = form,
        competitions = competitions.all(),
        categories = rq.get_all_categories(),
        armes = rq.get_all_armes(),
        to_date = cst.TO_DATE
    )

@app.route("/search_compet/", methods =("POST",))
def search_compet() :
    """Fonction qui permet d'afficher la page de recherche d'une compétition

    Returns:
        flask.Response: Renvoie la page de recherche d'une compétition
    """
    form = SearchForm()
    content_searched = form.searched.data
    if content_searched == "":
        return home()
    competitions = (Competition.query.filter(Competition.nom.like('%' + content_searched + '%'))
                    .order_by(Competition.nom).all())
    return render_template (
    "search.html",
    form=form,
    searched = content_searched,
    title = "Search Page",
    competitions = competitions)

@app.route("/informations")
def informations() :
    """Fonction qui permet d'afficher la page d'informations

    Returns:
        flask.Response: Renvoie la page d'informations
    """
    return render_template(
        "informations.html"
    )

class LoginForm(FlaskForm) :
    """Classe formulaire pour la connexion d'un utilisateur.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.

    Returns:
        flask.Response: Renvoie la page de connexion
    """
    num_licence = StringField('num_licence', validators=[DataRequired()])
    mot_de_passe = PasswordField("Password", validators=[DataRequired()])
    next = HiddenField()

    def get_authenticated_user(self) :
        """Fonction qui permet de récupérer un utilisateur authentifié.

        Returns:
            Escrimeur: Renvoie un utilisateur authentifié
        """
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        passwd =sha256(self.mot_de_passe.data.encode()).hexdigest()
        return user if passwd == user.mot_de_passe else None

class SignUpForm(FlaskForm) :
    """Classe formulaire pour l'inscription d'un utilisateur.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.

    Returns:
        flask.Response: Renvoie la page d'inscription
    """
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

    def get_authenticated_user(self) :
        """Fonction qui permet de récupérer un utilisateur authentifié.

        Returns:
            Escrimeur: Renvoie un utilisateur authentifié
        """
        user = Escrimeur.query.get(self.num_licence.data)
        if user is None:
            return None
        passwd =sha256(self.mot_de_passe.data.encode()).hexdigest()
        return user if passwd == user.mot_de_passe else None

    def est_deja_inscrit_sans_mdp(self) :
        """Fonction qui permet de vérifier si un utilisateur est déjà inscrit sans mot de passe.

        Returns:
            bool: Renvoie True si l'utilisateur est déjà inscrit sans mot de passe, False sinon
        """
        user = Escrimeur.query.get(self.num_licence.data)
        sexe = "Homme"
        if user is not None:
            if self.sexe.data == "Femme":
                sexe = "Dames"
            check_sexe = user.sexe == sexe
            check_prenom = user.prenom.upper() == self.prenom.data.upper()
            check_nom = user.nom.upper() == self.nom.data.upper()
            if check_sexe and check_prenom and check_nom:
                sha256().update(self.mot_de_passe.data.encode())
                passwd= sha256().hexdigest()
                user.set_mdp(passwd)
                db.session.commit()
                return True
            return False
        return None

@app.route("/connexion/", methods=("GET", "POST"))
def connexion() :
    """Fonction qui permet de gérer la connexion d'un utilisateur.

    Returns:
        flask.Response: Renvoie la page de connexion
    """
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
        print('test')
        user = form.get_authenticated_user()
        print(user)
        if user:
            login_user(user)
            prochaine_page = form.next.data or url_for("home")
            return redirect(prochaine_page)
    return render_template(
        "connexion.html",formlogin=form, formsignup = form2
        )

@app.route("/connexion/inscription", methods=("GET", "POST"))
def inscription() :
    """Fonction qui permet de gérer l'inscription d'un utilisateur.

    Returns:
        flask.Response: Renvoie la page d'inscription
    """
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
def affiche_competition(id_compet) :
    """Fonction qui permet d'afficher une compétition

    Args:
        id_compet (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page de la compétition
    """
    form = InscriptionForm()
    competition = rq.get_competition(id_compet)
    try :
        user = current_user.num_licence
    except AttributeError:
        user = -1
    return render_template(
        "competition.html",
        competition = competition, form = form, user = competition.est_inscrit(user),get_tireur=rq.get_tireur,dico = competition.get_tireurs_classes(),dicopoule = competition.get_tireurs_classes_poule()
    )

@app.route("/competition/<int:id_compet>/createPoule")
def competition_cree_poules(id_compet) :
    """Fonction qui permet de créer les poules d'une compétition

    Args:
        id_compet (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page de la compétition
    """
    competition = rq.get_competition(id_compet)
    competition.programme_poules()
    return redirect(url_for("affiche_competition", id_compet=id_compet))

@app.route("/competition/<int:id_compet>/phaseSuivante")
def phaseSuivante(id_compet) :
    """Fonction qui permet de créer les poules d'une compétition

    Args:
        id_compet (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page de la compétition
    """
    competition = rq.get_competition(id_compet)
    competition.programme_tableau()
    return redirect(url_for("affiche_competition", id_compet=id_compet))

@app.route("/competition/<int:id_compet>/poule/<int:id_poule>")
def affiche_poule(id_compet, id_poule) :
    """Fonction qui permet d'afficher une poule

    Args:
        id_compet (int): Identifiant unique de la compétition.
        id_poule (int): Identifiant unique de la poule.

    Returns:
        flask.Response: Renvoie la page de la poule
    """
    competition = rq.get_competition(id_compet)
    poule = competition.phases[id_poule-1]
    return render_template(
        "poule.html",
        competition = competition,
        poule = poule,
        constants = cst
    )

@app.route("/deconnexion/")
def deconnexion() :
    """Fonction qui permet de gérer la déconnexion d'un utilisateur.

    Returns:
        flask.Response: Renvoie la page d'accueil
    """
    logout_user()
    return redirect(url_for("home"))

@app.route('/cree/competition', methods=("GET", "POST"))
@login_required
def creation_competition() :
    """Fonction qui permet de créer une compétition.

    Returns:
        flask.Response: Renvoie la page de création d'une compétition
    """
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
        if sexe == "Hommes":
            sexe = "Homme"
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
def profil() :
    """Fonction qui permet d'afficher le profil d'un utilisateur.

    Returns:
        flask.Response: Renvoie la page du profil
    """
    return render_template(
        "profil.html",
        to_date = cst.TO_DATE,
        rq = rq
    )

class ChangerMdpForm(FlaskForm) :
    """Classe formulaire pour le changement de mot de passe d'un utilisateur.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.
    """
    new_mdp = PasswordField("Password",validators=[DataRequired()])
    next = HiddenField()

@app.route("/profil/changer-mdp", methods=("POST",))
def changer_mdp() :
    """Fonction qui permet de gérer le changement de mot de passe d'un utilisateur.

    Returns:
        flask.Response: Renvoie la page du profil
    """
    form =ChangerMdpForm()
    return render_template("changer-mdp.html", form=form)

@app.route("/shutdown", methods=['GET'])
def shutdown() :
    """Fonction qui permet d'arrêter le serveur.

    Returns:
        flask.Response: Renvoie un message de confirmation
    """
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({"success": True, "message": "Server is shutting down..."})

class InscriptionForm(FlaskForm) :
    """Classe formulaire pour l'inscription d'un utilisateur à une compétition.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.
    """
    role = RadioField('Role', choices = ['Arbitre','Tireur'])
    next = HiddenField()

@app.route("/competition/<int:id_compet>/inscription", methods=("GET", "POST"))
@login_required
def inscription_competition(id_compet) :
    """Fonction qui permet de gérer l'inscription d'un utilisateur à une compétition spécifique.

    Args:
        id_compet (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page de la compétition
    """
    form = InscriptionForm()
    competition = rq.get_competition(id_compet)
    inscrit = competition.est_inscrit(current_user.num_licence)
    try :
        user = current_user.num_licence
    except AttributeError:
        user = -1
    if not form.is_submitted() :
        form.next.data = request.args.get("next")
    else :
        if form.role.data == "Arbitre" and not inscrit :
            competition.inscription(current_user.num_licence,True)
            flash('Vous êtes inscrit comme arbitre', 'success')
            return redirect(url_for('affiche_competition',id_compet = id_compet))
        if form.role.data == "Tireur" and not inscrit :
            competition.inscription(current_user.num_licence)
            flash('Vous êtes inscrit comme tireur', 'success')
            return redirect(url_for('affiche_competition', id_compet = id_compet))
        flash('Vous êtes déja inscrit', 'danger')
        return redirect(url_for('affiche_competition', id_compet = id_compet))
    return render_template('competition.html',
        competition = competition, form = form, user = competition.est_inscrit(user),get_tireur=rq.get_tireur,dico = competition.get_tireurs_classes(),dicopoule = competition.get_tireurs_classes_poule()
)

@app.route("/suppr-competition/<int:id_compet>")
@login_required
def suppr_competition(id_compet : int) :
    """Fonction qui permet de supprimer une compétition.

    Args:
        id_compet (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page d'accueil
    """
    if current_user.is_admin() :
        rq.delete_competition(id_compet)
        flash('Compétition supprimée avec succès', 'warning')
    return redirect(url_for('home'))

class BracketForm(FlaskForm):
    """Classe formulaire pour la verification d'un match à élimination.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.
    """
    touches1 = IntegerField('touches1',validators=[DataRequired(), NumberRange(max=cst.TOUCHES_BRACKET, min=0)])
    touches2 = IntegerField('touches2',validators=[DataRequired(), NumberRange(max=cst.TOUCHES_BRACKET, min=0)])
    next=HiddenField()

class PouleForm(FlaskForm):
    """Classe formulaire pour la verification d'un match de poule.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.
    """
    touches1 = IntegerField('touches1',validators=[DataRequired(), NumberRange(max=cst.TOUCHES_POULE, min=0)])
    touches2 = IntegerField('touches2',validators=[DataRequired(), NumberRange(max=cst.TOUCHES_POULE, min=0)])
    next=HiddenField()

class StartForm(FlaskForm):
    """Classe formulaire pour le début d'un match.

    Args:
        FlaskForm (FlaskForm): Classe formulaire de Flask.
    """
    next=HiddenField()

@app.route("/competition/<int:id_compet>/poule/<int:id_poule>/match/<int:id_match>", methods=("GET", "POST"))
@login_required
def affiche_match(id_compet, id_poule, id_match):
    """Fonction qui permet d'afficher un match.

    Args:
        id_compet (int): Identifiant unique de la compétition.
        id_poule (int): Identifiant unique de la poule.
        id_match (int): Identifiant unique du match.

    Returns:
        flask.Response: Renvoie la page du match
    """
    competition = rq.get_competition(id_compet)
    poule = competition.get_phases_id(id_poule)

    if current_user.is_arbitre(id_compet) or current_user.is_admin() :
        match = poule.get_match_id(id_match)
        participations = match.get_tireurs_match(poule.id)
        if match.id_phase == 1:
            form_match = PouleForm()
        else:
            form_match = BracketForm()
        form_start = StartForm()
        if form_start.is_submitted():
            form_start.next.data = request.args.get("next")
            match.set_en_cours()
        return render_template(
            "match.html",
            competition = competition, 
            poule = poule, 
            match = match,
            participations = participations,
            constants = cst,
            form_match = form_match,
            form_start = form_start
        )
    else:
        return abort(401)

@app.route("/competition/<int:id_compet>/poule/<int:id_poule>/match/<int:id_match>/valider", methods=("GET", "POST"))
def valide_resultats(id_compet, id_poule, id_match):
    """Fonction qui permet de valider les résultats d'un match.

    Args:
        id_compet (int): Identifiant unique de la compétition.
        id_poule (int): Identifiant unique de la poule.
        id_match (int): Identifiant unique du match.

    Returns:
        flask.Response: Renvoie la page du match ou de la compétition
    """
    competition = rq.get_competition(id_compet)
    poule = competition.get_phases_id(id_poule)
    match = poule.get_match_id(id_match)
    participations = match.get_tireurs_match(poule.id)
    if match.id_phase == 1:
        form_match = PouleForm()
    else:
        form_match = BracketForm()
    if not form_match.is_submitted():
        form_match.next.data = request.args.get("next")
    else:
        tireur1, tireur2 = (participations[0].id_escrimeur,form_match.touches1.data),(participations[1].id_escrimeur,form_match.touches2.data)

        vainqueur = tireur1 if tireur1[1] > tireur2[1] else tireur2
        perdant = tireur1 if tireur1[1] < tireur2[1] else tireur2

        match.valide_resultat(vainqueur, perdant)
        return redirect(url_for("affiche_poule", id_compet=id_compet, id_poule=id_poule))
    form_start = StartForm()
    return render_template(
        "match.html",
        competition = competition,
        poule = poule,
        match = match,
        participations = match.get_tireurs_match(poule.id),
        form_match = form_match,
        form_start = form_start
    )

@app.route("/competition/<int:id_compet>/deinscription", methods=("GET", "POST"))
def deinscription_competition(id_compet : int) :
    """Fonction qui permet de gérer la désinscription d'un utilisateur à une compétition spécifique

    Args:
        id_compet (int): Identifiant unique de la compétition.

    Returns:
        flask.Response: Renvoie la page de la compétition
    """
    form = InscriptionForm()
    competition = rq.get_competition(id_compet)
    competition.desinscription(current_user.num_licence)
    try :
        user = current_user.num_licence
    except AttributeError:
        user = -1
    flash('Vous êtes désinscrit', 'warning')
    return render_template('competition.html',
    competition = competition, form = form, user = competition.est_inscrit(user),get_tireur=rq.get_tireur,dico = competition.get_tireurs_classes(),dicopoule = competition.get_tireurs_classes_poule()
)

@app.route("/competition/<int:id_compet>/affichage-grand-ecran", methods=("GET", "POST"))
def affichage_grand_ecran(id_compet) :
    competition = rq.get_competition(id_compet)
    flash('Vous êtes désinscrit', 'warning')

    return render_template('affichageGE.html',
                           competition=competition,get_tireur = rq.get_tireur)

@app.errorhandler(Exception)
def page_not_found(erreur) :
    """Fonction qui permet de gérer les erreurs.

    Args:
        erreur (Exception): Erreur qui est levée.

    Returns:
        flask.Response: Renvoie la page d'erreur
    """
    return render_template('erreur.html', code=erreur.code, message=erreur.__class__.__name__), erreur.code
