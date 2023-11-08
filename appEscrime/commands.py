"""Module contenant les commandes de l'application."""
from datetime import datetime
from hashlib import sha256
import click
import csv
import os
from .app import app , db
from .models import *

@app.cli.command()
def loadbd():
    """Creates the tables and populates them with data."""

    # création de toutes les tables
    db.create_all()

    # création du type de phase de poule
    types_phase = {'Poule': Type_phase(libelle = 'Poule', nb_touches = 5)}
    for type_phase in types_phase.values():
        db.session.add(type_phase)

    # création des 3 armes possibles
    armes = {'Fleuret': Arme(libelle = 'Fleuret'),
             'Epée': Arme(libelle = 'Epée'),
             'Sabre': Arme(libelle = 'Sabre')}
    for arme in armes.values():
        db.session.add(arme)

    # création des 9 catégories possibles
    categories = {'M13': Categorie(libelle = 'M13', age_maxi = 13),
                  'M15': Categorie(libelle = 'M15', age_maxi = 15),
                  'M17': Categorie(libelle = 'M17', age_maxi = 17),
                  'M20': Categorie(libelle = 'M20', age_maxi = 20),
                  'Seniors': Categorie(libelle = 'Seniors', age_maxi = 39),
                  'Vétérans1': Categorie(libelle = 'Vétérans1', age_maxi = 49),
                  'Vétérans2': Categorie(libelle = 'Vétérans2', age_maxi = 59),
                  'Vétérans3': Categorie(libelle = 'Vétérans3', age_maxi = 69),
                  'Vétérans4': Categorie(libelle = 'Vétérans4', age_maxi = -1)}
    for categorie in categories.values():
        db.session.add(categorie)
    
    # création de l'instance de club permettant d'identifier les administrateurs
    clubs = {'CEB Admin': Club(nom = 'CEB Admin'),
             'Aucun club': Club(nom = 'Aucun club')}
    for club in clubs.values():
        db.session.add(club)

    db.session.commit()

    escrimeurs = dict()
    lieux = dict()
    competitions = dict()

    # chargement de toutes les données
    for nom_fichier in os.listdir('../data'): # Éxecution dans appEscrime
        with open('../data/' + nom_fichier, newline = '', encoding = 'Latin-1') as fichier:
            nom_fichier = nom_fichier[:-4]
            print(nom_fichier)
            lecteur = csv.DictReader(fichier, delimiter = ';')
            contenu = nom_fichier.split('_')
            
            if contenu[0] == 'classement':
                if '-' in contenu[3]:
                    split_cat = contenu[3].split('-')
                    contenu[3] = split_cat[0][:-1] + split_cat[-1]
                for ligne in lecteur:
                    print(ligne)
                    
                    nom_club = ligne['club']
                    if nom_club not in clubs:
                        club = Club(nom = nom_club)
                        clubs[nom_club] = club
                        db.session.add(club)
                    
                    licence = ligne['adherent']
                    if licence not in escrimeurs:
                        naissance = ligne['date naissance'].split('/')
                        club = clubs[ligne['club']]
                        escrimeur = Escrimeur(num_licence = licence,
                                              prenom = ligne['prenom'],
                                              nom = ligne['nom'],
                                              sexe = contenu[2],
                                              date_naissance = datetime(int(naissance[2]), int(naissance[1]), int(naissance[0])),
                                              id_club = club.id)
                        escrimeurs[licence] = escrimeur
                        db.session.add(escrimeur)

                    arme = armes[contenu[1]]
                    categorie = categories[contenu[3]]
                    escrimeur = escrimeurs[ligne['adherent']]
                    db.session.add(Classement(classement = ligne['rang'],
                                              points = ligne['points'],
                                              num_licence = escrimeur.num_licence,
                                              id_arme = arme.id,
                                              id_categorie = categorie.id))
                    
            elif contenu[0] == 'connexion':
                for ligne in lecteur:
                    mdp = ligne['mdp']
                    escrimeur = escrimeurs[ligne['adherent']]
                    escrimeur.set_mdp(mdp)
            
            elif contenu[0] == 'competitions':
                for ligne in lecteur:
                    nom_lieu = ligne['lieu']
                    if nom_lieu not in lieux:
                        lieu = Lieu(nom = nom_lieu, adresse = ligne['adresse'])
                        lieux[nom_lieu] = lieu
                        db.session.add(lieu)

                    date_compet = ligne['date'].split('/')
                    arme = armes[ligne['arme']]
                    categorie = categories[ligne['categorie']]
                    lieu = lieux[ligne['lieu']]
                    competition = Competition(nom = ligne['nom'],
                                              date = datetime(int(date_compet[2]), int(date_compet[1]), int(date_compet[0])),
                                              coefficient = ligne['coefficient'],
                                              id_arme = arme.id,
                                              id_categorie = categorie.id,
                                              id_lieu = lieu.id
                                              )
                    competitions[ligne['nom']] = competition
                    db.session.add(competition)
                    
            db.session.commit()



@app.cli.command()
def syncbd():
    """Crée les tables de la base de données"""
    db.create_all()

@app.cli.command()
def deletebd():
    if os.path.exists('../CEB.db'):
        os.remove('../CEB.db')