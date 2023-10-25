"""Module contenant les commandes de l'application."""
from hashlib import sha256
import click
import os
from .app import app , db
from .models import *

@app.cli.command()
def loaddb():
    """Creates the tables and populates them with data."""

    # création de toutes les tables
    db.create_all()

    # création du type de phase de poule
    db.session.add(Type_phase(libelle = 'Poule', nb_touches = 5))

    # création des 3 armes possibles
    db.session.add(Arme(libelle = 'Fleuret'))
    db.session.add(Arme(libelle = 'Epée'))
    db.session.add(Arme(libelle = 'Sabre'))

    # création des 9 catégories possibles
    db.session.add(Categorie(libelle = 'M13', age_maxi = 13))
    db.session.add(Categorie(libelle = 'M15', age_maxi = 15))
    db.session.add(Categorie(libelle = 'M17', age_maxi = 17))
    db.session.add(Categorie(libelle = 'M20', age_maxi = 20))
    db.session.add(Categorie(libelle = 'Seniors', age_maxi = 39))
    db.session.add(Categorie(libelle = 'Vétérans1', age_maxi = 49))
    db.session.add(Categorie(libelle = 'Vétérans2', age_maxi = 59))
    db.session.add(Categorie(libelle = 'Vétérans3', age_maxi = 69))
    db.session.add(Categorie(libelle = 'Vétérans4', age_maxi = 1000))




    for filename in os.listdir('data'):
        # chargement de notre jeu de données
        with open(filename, 'r', encoding='utf-8') as file:
            books = yaml.safe_load(file)

        # première passe: création de tous les auteurs
        authors = {}
        for b in books:
            a = b["author"]
            if a not in authors:
                o = Author(name=a)
                db.session.add(o)
                authors[a] = o
                db.session.commit ()

        # deuxième passe: création de tous les livres
        for b in books:
            a = authors[b["author"]]
            o = Book(price = b["price"],
                    title = b["title"],
                    url = b["url"] ,
                    img = b["img"] ,
                    author_id = a.id)
        db.session.add(o)
    db.session.commit()

@app.cli.command()
def syncdb():
    """Creates the tables."""
    db.create_all()