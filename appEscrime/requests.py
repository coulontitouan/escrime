from sqlalchemy import desc
from .models import Lieu, Competition, Phase, Match, Participation, Resultat, Club, Phase, TypePhase, Arme, Categorie
from .app import db

def get_all_armes():
    """Récupère toutes les armes dans la base de données"""
    return Arme.query.all()

def get_all_categories():
    """Récupère toutes les catégories dans la base de données"""
    return Categorie.query.all()

def get_all_competitions():
    """Récupère toutes les compétitions dans la base de données"""
    return Competition.query.all()

def get_arme(id):
    """Récupère une arme dans la base de données à partir de son id
    
    Args:
        id (int): l'id d'une arme
    """
    return Arme.query.get(id)

def get_club(id):
    """Récupère un club dans la base de données à partir de son id
    
    Args:
        id (int): l'id d'un club
    """
    return Club.query.get(id)

def get_categorie(id):
    """Récupère une catégorie dans la base de données à partir de son id
    
    Args:
        id (int): l'id d'une catégorie
    """
    return Categorie.query.get(id)

def get_competition(id):
    """Récupère une compétition dans la base de données à partir de son id
    
    Args:
        id (int): l'id d'une compétition
    """
    return Competition.query.get(id)

def get_participation(id):
    """Récupère une participation dans la base de données à partir de son id
    
    Args:
        id (int): l'id d'une participation
    """
    return Participation.query.get(id)

def get_match(id):
    """Récupère un match dans la base de données à partir de son id
    
    Args:
        id (int): l'id d'un match
    """
    return Match.query.get(id)

def get_typephase(id):
    """Récupère un type de phase dans la base de données à partir de son id
    
    Args:
        id (int): l'id d'un type de phase
    """
    return TypePhase.query.get(id)

def get_max_competition_id():
    """Récupère l'id de la dernière compétition créée"""
    if Competition.query.count() == 0:
        return 0
    return Competition.query.order_by(desc(Competition.id)).first().ids

def get_lieu(nom, adresse, ville):
    """Récupère un lieu dans la base de données à partir de son nom, son adresse et sa ville
    
    Args:
        nom (str): le nom d'un lieu
        adresse (str): l'adresse d'un lieu
        ville (str): la ville d'un lieu
    """
    return Lieu.query.filter_by(nom = nom, adresse = adresse, ville = ville).first()

def get_tireurs_competition(id_compet):
    """Récupère tous les tireurs d'une compétition à partir de son id
    
    Args:
        id_compet (int): l'id d'une compétition
    """
    return get_competition(id_compet).get_tireurs()

def get_est_inscrit(num_licence, id_competition):
    """Vérifie si un tireur donné est inscrit à une compétition donnée
    
    Args:
        num_licence (int): le numéro de licence d'un tireur
        id_competition (int): l'id d'une compétition
    """
    a = Resultat.query.filter_by(id_competition = id_competition, id_escrimeur = num_licence).first()
    if a is None :
        return False
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

def cree_liste_nom_objet(liste):
    """Crée une liste de tuples (id, libelle) à partir d'une liste d'objets
    
    Args:
        liste (list): une liste d'objets
    """
    cpt = 1
    liste2 = []
    for x in liste :
        liste2.append((cpt, x.libelle))
        cpt += 1
    return liste2