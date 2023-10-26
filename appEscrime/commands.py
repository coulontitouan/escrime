"""Module contenant les commandes de l'application."""
from datetime import datetime
from hashlib import sha256
import click
import csv
import os
from .app import app , db
from .models import *

@app.cli.command()
def load_bd():
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
    clubs = {'CEB Admin': Club(nom = 'CEB Admin')}

    db.session.commit()

    escrimeurs = dict()

    # chargement de toutes les données
    for nom_fichier in os.listdir('data'):
        with open(nom_fichier, newline = '', encoding = 'utf-8') as fichier:
            lecteur = csv.DictReader(fichier)
            contenu = nom_fichier.split('_')
            if '-' in contenu[3]:
                split_cat = contenu[3].split('-')
                contenu[3] = split_cat[1][:-1] + split_cat[-1]
            
            if contenu[0] == 'classement':
                
                for ligne in lecteur:
                    
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
                                              club_id = club.id,
                                              mot_de_passe = '')
                        escrimeurs[licence] = escrimeur
                        db.session.add(escrimeur)

                    arme = armes[contenu[1]]
                    categorie = categories[contenu[3]]
                    escrimeur = escrimeurs[ligne['adherent']]
                    db.session.add(Categorisation(classement = ligne['rang'],
                                                  points = ligne['points'],
                                                  num_licence = escrimeur.num_licence,
                                                  id_arme = arme.id,
                                                  id_categorie = categorie.id))
                    
                    db.session.commit()
            
            elif contenu[0] == 'connexion':

                for ligne in lecteur:

                    mdp = ligne['mdp']
                    escrimeur = escrimeurs[ligne['adherent']]
                    escrimeur.set_mdp(mdp)



@app.cli.command()
def syncdb():
    """Creates the tables."""
    db.create_all()