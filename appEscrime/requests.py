from sqlalchemy import desc
from .models import Lieu, Competition, Phase, Match, Participation, Resultat, Club, Phase, TypePhase, Arme, Categorie
from .app import db

def get_lieu(nom, adresse, ville):
    """Fonction qui permet de récupérer un lieu dans la base de données"""
    return Lieu.query.filter_by(nom = nom, adresse = adresse, ville = ville).first()

def get_arme(id):
    """Fonction qui permet de récupérer une arme dans la base de données"""
    return Arme.query.get(id)

def get_all_armes():
    """Fonction qui permet de récupérer toutes les armes dans la base de données"""
    return Arme.query.all()

def get_club(id):
    return Club.query.get(id)

def get_categorie(id):
    """Fonction qui permet de récupérer une catégorie dans la base de données"""
    return Categorie.query.get(id)

def get_all_categories():
    """Fonction qui permet de récupérer toutes les catégories dans la base de données"""
    return Categorie.query.all()

def get_max_competition_id():
    """Fonction qui permet de récupérer l'id de la dernière compétition créée"""
    if Competition.query.count() == 0:
        return 0
    return Competition.query.order_by(desc(Competition.id)).first().id

def get_compet_accueil():
    return Competition.query.all()

def get_competition(id):
    return Competition.query.get(id)

def get_all_competitions():
    return Competition.query.all()

def get_tireurs_competition(id_compet):
    return get_competition(id_compet).get_tireurs()

def get_participation(id):
    return Participation.query.get(id)

def get_match(id):
    return Match.query.get(id)

def get_typephase(id):
    return TypePhase.query.get(id)

def get_est_inscrit(num_licence, id_competition):
    a = Resultat.query.filter_by(id_competition = id_competition, id_escrimeur = num_licence).first()
    if a == None :
        return False
    else:
        return True

def delete_competition(id):
    """Supprime une compétion dans la BD à partir de son id

    Args:
        id (int): l'id d'une compétition
    """
    Participation.query.filter(Participation.id_competition == id).delete()
    Match.query.filter(Match.id_competition == id).delete()
    Phase.query.filter(Phase.id_competition == id).delete()
    Resultat.query.filter(Resultat.id_competition == id).delete()
    Competition.query.filter(Competition.id == id).delete()
    db.session.commit()

def cree_liste(liste) :
    cpt = 1
    liste2 = []
    for x in liste :
        liste2.append((cpt, x.libelle))
        cpt += 1
    return liste2