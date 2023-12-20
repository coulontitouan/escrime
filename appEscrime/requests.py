"""Module contenant les fonctions de requêtes à la base de données."""

from sqlalchemy import desc
from .models import Lieu, Competition, Phase, Match, Participation, Resultat, Club, TypePhase, Arme, Categorie # pylint: disable=line-too-long
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

def get_arme(id_arme):
    """Récupère une arme dans la base de données à partir de son id

    Args:
        id_arme (int): l'id d'une arme
    """
    return Arme.query.get(id_arme)

def get_arme_par_libelle(libelle):
    """Fonction qui permet de récupérer une arme à partir de son libellé dans la base de données

    Args:
        libelle (str): le libellé d'une arme
    """
    return Arme.query.filter(Arme.libelle == libelle).first()

def get_club(id_club):
    """Récupère un club dans la base de données à partir de son id

    Args:
        id_club (int): l'id d'un club
    """
    return Club.query.get(id_club)

def get_categorie(id_cat):
    """Récupère une catégorie dans la base de données à partir de son id

    Args:
        id_cat (int): l'id d'une catégorie
    """
    return Categorie.query.get(id_cat)

def get_categorie_par_libelle(libelle):
    """Fonction qui permet de récupérer une catégorie à partir de son libellé dans la base de données

    Args:
        libelle (str): le libellé d'une categorie
    """
    return Categorie.query.filter(Categorie.libelle == libelle).first()

def get_competition(id_compet):
    """Récupère une compétition dans la base de données à partir de son id

    Args:
        id_compet (int): l'id d'une compétition
    """
    return Competition.query.get(id_compet)

def get_participation(id_part):
    """Récupère une participation dans la base de données à partir de son id

    Args:
        id_part (int): l'id d'une participation
    """
    return Participation.query.get(id_part)

def get_match(id_match):
    """Récupère un match dans la base de données à partir de son id

    Args:
        id_match (int): l'id d'un match
    """
    return Match.query.get(id_match)

def get_type_phase(id_type):
    """Récupère un type de phase dans la base de données à partir de son id

    Args:
        id_type (int): l'id d'un type de phase
    """
    return TypePhase.query.get(id_type)

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

def get_est_inscrit(num_licence, id_compet):
    """Vérifie si un tireur donné est inscrit à une compétition donnée

    Args:
        num_licence (int): le numéro de licence d'un tireur
        id_compet (int): l'id d'une compétition
    """
    requete = Resultat.query.filter_by(id_competition = id_compet,
                                 id_escrimeur = num_licence).first()
    if requete is None :
        return False
    return True

def delete_competition(id_compet):
    """Supprime une compétion dans la BD à partir de son id

    Args:
        id_compet (int): l'id d'une compétition
    """
    Participation.query.filter(Participation.id_competition == id_compet).delete()
    Match.query.filter(Match.id_competition == id_compet).delete()
    Phase.query.filter(Phase.id_competition == id_compet).delete()
    Resultat.query.filter(Resultat.id_competition == id_compet).delete()
    Competition.query.filter(Competition.id == id_compet).delete()
    db.session.commit()

def cree_liste_nom_objet(liste):
    """Crée une liste de tuples (id, libelle) à partir d'une liste d'objets

    Args:
        liste (list): une liste d'objets
    """
    cpt = 1
    liste2 = []
    for element in liste :
        liste2.append((cpt, element.libelle))
        cpt += 1
    return liste2
