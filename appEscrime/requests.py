"""Module contenant les fonctions de requêtes à la base de données."""

from sqlalchemy import desc
from .models import Lieu, Competition, Phase, Match, Participation, Resultat, Club, TypePhase, Arme, Categorie, Escrimeur # pylint: disable=line-too-long
from .app import db

def get_all_armes()-> list[Arme]:
    """Récupère toutes les armes dans la base de données"""
    return Arme.query.all()

def get_all_categories()->list[Categorie]:
    """Récupère toutes les catégories dans la base de données"""
    return Categorie.query.all()

def get_arme(id_arme)->Arme:
    """Récupère une arme dans la base de données à partir de son id

    Args:
        id_arme (int): l'id d'une arme
    """
    return Arme.query.get(id_arme)

def get_arme_par_libelle(libelle)->Arme:
    """Fonction qui permet de récupérer une arme à partir de son libellé dans la base de données

    Args:
        libelle (str): le libellé d'une arme
    """
    return Arme.query.filter(Arme.libelle == libelle).first()

def get_club(id_club) -> Club:
    """Récupère un club dans la base de données à partir de son id

    Args:
        id_club (int): l'id d'un club
    """
    return Club.query.get(id_club)

def get_categorie(id_cat)->Categorie:
    """Récupère une catégorie dans la base de données à partir de son id

    Args:
        id_cat (int): l'id d'une catégorie
    """
    return Categorie.query.get(id_cat)

def get_categorie_par_libelle(libelle)->Categorie:
    """Fonction qui permet de récupérer une catégorie à partir de son libellé dans la base de données

    Args:
        libelle (str): le libellé d'une categorie
    """
    return Categorie.query.filter(Categorie.libelle == libelle).first()

def get_competition(id_compet)->Competition:
    """Récupère une compétition dans la base de données à partir de son id

    Args:
        id_compet (int): l'id d'une compétition
    """
    return Competition.query.get(id_compet)

def get_participation(id_part)->Participation:
    """Récupère une participation dans la base de données à partir de son id

    Args:
        id_part (int): l'id d'une participation
    """
    return Participation.query.get(id_part)

def get_tireur(num_licence)->Escrimeur:
    """Récupère un tireur dans la base de données à partir de son numéro de licence

    Args:
        id_part (num_licence): le numéro de licence d'un tireur
    """
    return Escrimeur.query.get(num_licence)

def get_max_competition_id()->int:
    """Récupère l'id de la dernière compétition créée"""
    if Competition.query.count() == 0:
        return 0
    return Competition.query.order_by(desc(Competition.id)).first().id

def get_lieu(nom, adresse, ville)->Lieu:
    """Récupère un lieu dans la base de données à partir de son nom, son adresse et sa ville

    Args:
        nom (str): le nom d'un lieu
        adresse (str): l'adresse d'un lieu
        ville (str): la ville d'un lieu
    """
    return Lieu.query.filter_by(nom = nom, adresse = adresse, ville = ville).first()

def delete_competition(id_compet:int)->None:
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

def cree_liste_nom_objet(liste)->list:
    """Crée une liste de tuples (id, libelle) à partir d'une liste d'objets

    Args:
        liste (list): une liste d'objets
    """
    return [(i+1, liste[i].libelle) for i in range(len(liste))]
