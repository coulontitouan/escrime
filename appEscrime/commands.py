"""Module contenant les commandes de l'application."""
from datetime import datetime
import csv
import os
import click
import appEscrime.constants as cst
import getpass
from .app import app , db
from .models import Match, TypePhase, Arme, Categorie, Club, Escrimeur, Competition
from .populates import load_competitions,load_connexion,load_escrimeurs,load_matchs,load_resultats
from .populates import save_competitions, save_classements, save_connexions

DB_DIR = './CEB.db'

@app.cli.command()
def loadbd():
    """Crée les tables et gère le peuplement de la base de données"""

    if os.path.exists(DB_DIR):
        os.remove(DB_DIR)
    # création de toutes les tables
    db.create_all()

    # création des 3 armes possibles
    armes = {'Fleuret': Arme(libelle = 'Fleuret'),
             'Epée': Arme(libelle = 'Epée'),
             'Sabre': Arme(libelle = 'Sabre')}
    for arme in armes.values():
        db.session.add(arme)

    # création des 9 catégories possibles
    categories = {'M13': Categorie(libelle = 'M13', age_maxi = cst.AGE_MAX_M13),
                  'M15': Categorie(libelle = 'M15', age_maxi = cst.AGE_MAX_M15),
                  'M17': Categorie(libelle = 'M17', age_maxi = cst.AGE_MAX_M17),
                  'M20': Categorie(libelle = 'M20', age_maxi = cst.AGE_MAX_M20),
                  'Seniors': Categorie(libelle = 'Seniors', age_maxi = cst.AGE_MAX_SENIORS),
                  'Vétérans1': Categorie(libelle = 'Vétérans1', age_maxi = cst.AGE_MAX_VETERANS1),
                  'Vétérans2': Categorie(libelle = 'Vétérans2', age_maxi = cst.AGE_MAX_VETERANS2),
                  'Vétérans3': Categorie(libelle = 'Vétérans3', age_maxi = cst.AGE_MAX_VETERANS3),
                  'Vétérans4': Categorie(libelle = 'Vétérans4', age_maxi = cst.AGE_MAX_VETERANS4)}
    for categorie in categories.values():
        db.session.add(categorie)

    # création de l'instance de club permettant d'identifier les administrateurs
    clubs = {'CEB Admin': Club(nom = 'CEB Admin'),
             'Aucun club': Club(nom = 'Aucun club')}
    for club in clubs.values():
        db.session.add(club)

    # création du type de phase de poule
    types_phase = {'Poule': TypePhase(libelle = 'Poule', touches_victoire = cst.TOUCHES_POULE)}
    for type_phase in types_phase.values():
        db.session.add(type_phase)

    db.session.commit()

    escrimeurs = {}
    competitions = {}
    lieux = {}
    phases = {}

    # chargement de toutes les données
    les_fichiers = os.listdir('./data') # Éxecution dans appEscrime
    les_fichiers.sort()
    for nom_fichier in les_fichiers:
        if os.path.splitext(nom_fichier)[1] == '.csv':
            with open('./data/' + nom_fichier, 'r', newline = '', encoding = 'utf-8') as fichier:
                nom_fichier = nom_fichier[:-4]
                print(nom_fichier)
                lecteur = csv.DictReader(fichier, delimiter = ';')
                contenu = nom_fichier.split('_')

                if contenu[0] == 'classement':
                    load_escrimeurs(contenu, lecteur, escrimeurs, clubs, armes, categories)

                elif contenu[0] == 'connexion':
                    load_connexion(lecteur, escrimeurs)

                elif contenu[0] == 'competitions':
                    load_competitions(lecteur, armes, categories, competitions, lieux)

                elif contenu[0] == 'matchs':
                    load_matchs(contenu, lecteur, escrimeurs, competitions, phases, types_phase)

                elif contenu[0] == 'resultats':
                    load_resultats(contenu, lecteur)
            fichier.close()
        db.session.commit()

@app.cli.command()
def syncbd():
    """Crée les tables de la base de données"""
    db.create_all()

@app.cli.command()
def deletebd():
    """Supprime la base de données"""
    if os.path.exists(DB_DIR):
        os.remove(DB_DIR)

@app.cli.command()
def savebd():
    """Sauvegarde la base de données dans des fichiers csv"""
    for nom_fichier in os.listdir('./data'):
        if os.path.splitext(nom_fichier)[1] == '.csv':
            os.remove('./data/' + nom_fichier)
    save_classements()
    save_connexions()
    save_competitions()

def newuser(num_licence, password, prenom, nom, sexe, ddn, club):
    """Crée un nouvel utilisateur"""
    cst.CRYPTAGE.update(password.encode())
    tireur = Escrimeur(num_licence=num_licence,
                       mot_de_passe=cst.CRYPTAGE.hexdigest(),
                       prenom=prenom,
                       nom=nom,
                       sexe=sexe,
                       date_naissance=ddn,
                       id_club=club)
    db.session.add(tireur)
    db.session.commit()

@app.cli.command()
def newadmin():
    """Ajoute un admin"""
    prenom = input("Prénom : ")
    nom = input("Nom : ")
    mot_de_passe = getpass.getpass("Mot de passe : ")
    cst.CRYPTAGE.update(mot_de_passe.encode())
    date_convert = datetime.strptime('01/01/0001', cst.TO_DATE).date()
    db.session.add(Escrimeur(num_licence=prenom,
                  prenom=prenom,
                  nom=nom,
                  sexe="Admin",
                  date_naissance=date_convert,
                  id_club=cst.CLUB_ADMIN,
                  mot_de_passe=cst.CRYPTAGE.hexdigest()))
    db.session.commit()

@app.cli.command()
@click.argument('id_competition')
def test(id_competition):
    """Commande test développeur"""
    Competition.query.get(int(id_competition)).programme_poules()
    for mmatch in Match.query.filter_by(id_competition = id_competition).all():
        print(mmatch)
        print(mmatch.participations, '\n')
