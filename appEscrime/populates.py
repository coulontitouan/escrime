import csv
from datetime import datetime
import os

from sqlalchemy import and_
from .app import db
from .models import Classement, Lieu, Competition, Phase, Match, Participation, Resultat, Club, Escrimeur, Phase, Type_phase, Arme, Categorie

# def conversion_csv_utf8(chemin):
#     with open('../data/' + chemin, 'r', encoding = 'latin-1') as fichier_entree:
#         lecteur = csv.reader(fichier_entree, delimiter=';')
#         if os.path.exists('../data/.encoded/' + chemin):
#             os.remove('../data/.encoded/' + chemin)
#         for ligne in lecteur:
#             data = [carac for carac in ligne]
#             with open('../data/.encoded/' + chemin, 'a', newline = '', encoding = 'utf-8') as fichier_sortie:
#                 writer = csv.writer(fichier_sortie, delimiter=';')
#                 writer.writerow(data)
#             fichier_sortie.close()
#     fichier_entree.close()


def load_escrimeurs(contenu, lecteur, escrimeurs, clubs, armes, categories):
    """Charge les escrimeurs, classements, armes, catégories et clubs dans la base de données

    Args:
        contenu (list[String]): le contenu du fichier csv courant
        lecteur (DictReader): le lecteur du fichier csv courant
        escrimeurs (dict): le dictionnaire des escrimeurs déjà présents dans la base
        clubs (dict): le dictionnaire des clubs déjà présents dans la base
        armes (dict): le dictionnaire des armes déjà présentes dans la base
        categories (dict): le dictionnaire des catégories déjà présentes dans la base
    """

    if '-' in contenu[3]:
        split_cat = contenu[3].split('-')
        contenu[3] = split_cat[0][:-1] + split_cat[-1]

    for ligne in lecteur:
        nom_club = ligne['club']
        if nom_club not in clubs:
            club = Club(nom = nom_club,
                        region = ligne['comite regional'])
            clubs[nom_club] = club
            db.session.add(club)

        licence = ligne['adherent']
        if licence not in escrimeurs:
            naissance = ligne['date naissance'].split('/')
            club = clubs[nom_club]
            escrimeur = Escrimeur(num_licence = licence,
                                  prenom = ligne['prenom'],
                                  nom = ligne['nom'],
                                  sexe = contenu[2],
                                  nationalite = ligne['nation'],
                                  date_naissance = datetime(int(naissance[2]),
                                                            int(naissance[1]),
                                                            int(naissance[0])),
                                  club = club)
            escrimeurs[licence] = escrimeur
            db.session.add(escrimeur)

        arme = armes[contenu[1]]
        categorie = categories[contenu[3]]
        escrimeur = escrimeurs[ligne['adherent']]
        db.session.add(Classement(rang = ligne['rang'],
                                  points = ligne['points'],
                                  num_licence = escrimeur.num_licence,
                                  id_arme = arme.id,
                                  id_categorie = categorie.id))


def load_connexion(lecteur, escrimeurs):
    """Charge les informations de connexion dans la base de données

    Args:
        lecteur (DictReader): le lecteur du fichier csv courant
        escrimeurs (dict): le dictionnaire des escrimeurs déjà présents dans la base
    """
    for ligne in lecteur:
        mdp = ligne['mdp']
        escrimeur = escrimeurs[ligne['adherent']]
        escrimeur.set_mdp(mdp)


def load_competitions(lecteur, armes, categories, competitions, lieux):
    """Charge les compétitions dans la base de données

    Args:
        lecteur (DictReader): le lecteur du fichier csv courant
        categories (dict): le dictionnaire des catégories déjà présentes dans la base
        competitions (dict): le dictionnaire des compétitions déjà présentes dans la base
        lieux (dict): le dictionnaire des lieux déjà présents dans la base
    """
    for ligne in lecteur:
        nom_lieu = ligne['lieu']
        if nom_lieu not in lieux:
            lieu = Lieu(nom = nom_lieu,
                        adresse = ligne['adresse'],
                        ville = ligne['ville'])
            lieux[nom_lieu] = lieu
            db.session.add(lieu)

        date_compet = ligne['date'].split('/')
        arme = armes[ligne['arme']]
        categorie = categories[ligne['categorie']]
        lieu = lieux[ligne['lieu']]
        competition = Competition(nom = ligne['nom'],
                                  date = datetime(int(date_compet[2]),
                                                  int(date_compet[1]),
                                                  int(date_compet[0])),
                                  coefficient = ligne['coefficient'],
                                  sexe = ligne['sexe'],
                                  id_arme = arme.id,
                                  id_categorie = categorie.id,
                                  id_lieu = lieu.id
                                  )
        competitions[ligne['nom']] = competition
        db.session.add(competition)


def load_matchs(contenu, lecteur, escrimeurs, competitions, phases, types_phase):
    """Charge les matchs dans la base de données

    Args:
        contenu (list[String]): le contenu du fichier csv courant
        lecteur (DictReader): le lecteur du fichier csv courant
        escrimeurs (dict): le dictionnaire des escrimeurs déjà présents dans la base
        competitions (dict): le dictionnaire des compétitions déjà présentes dans la base
        phases (dict): le dictionnaire des phases de compétition déjà présentes dans la base
        types_phase (dict): le dictionnaire des types de phase déjà présents dans la base
    """
    for ligne in lecteur:
        nom_phase = ligne['libelle phase']
        if nom_phase not in types_phase:
            type_phase = Type_phase(libelle = nom_phase, nb_touches = 15)
            types_phase[nom_phase] = type_phase
            db.session.add(type_phase)

        concatenation_compet_phase = competitions[contenu[3]] + ligne['phase']
        if concatenation_compet_phase not in phases:
            phase = Phase(id = ligne['phase'],
                          id_competition = competitions[contenu[4]],
                          libelle = nom_phase)
            phases[concatenation_compet_phase] = phase
            db.session.add(phase)

            mmatch = Match(id = ligne['numero'],
                           id_competition = competitions[contenu[3]],
                           id_phase = ligne['phase'],
                           piste = ligne['piste'],
                           etat = ligne['etat'],
                           num_arbitre = escrimeurs[ligne['arbitre']].num_licence)
            db.session.add(mmatch)

            for i in range(1,3):
                escrimeur = escrimeurs[ligne['tireur' + i]]
                nb_touches = int(ligne['touches' + i])
                if ligne['etat'] == 'Termine':
                    if nb_touches == types_phase[ligne['libelle phase']].touches_victoire:
                        db.session.add(Participation(match = mmatch,
                                                     tireur = escrimeur,
                                                     touches = nb_touches,
                                                     statut = "Vainqueur"))
                    else:
                        db.session.add(Participation(match = mmatch,
                                                     tireur = escrimeur,
                                                     touches = nb_touches,
                                                     statut = "Perdant"))
                else:
                    db.session.add(Participation(match = mmatch,
                                                 tireur = escrimeur,
                                                 touches = nb_touches))


def load_resultats(contenu, lecteur):
    """Charge les résultats dans la base de données

    Args:
        contenu (list[String]): le contenu du fichier csv courant
        lecteur (DictReader): le lecteur du fichier csv courant
    """
    for ligne in lecteur:
        competition = contenu[3]
        db.session.add(Resultat(id_competition = competition,
                                id_escrimeur = ligne['adherent'],
                                rang = ligne['rang'],
                                points = ligne['points']))

def save_competitions():
    with open('../data/competitions_CEB.csv', 'w', encoding = 'utf-8') as fichier:
        writer = csv.writer(fichier, delimiter = ";")
        writer.writerow(['nom','date','sexe','categorie','arme','coefficient','lieu','ville','adresse'])
        for competition in Competition.query.all():
            writer.writerow(competition.to_csv())
    fichier.close()
    
    for competition in Competition.query.all():
        titre = competition.to_titre_csv()
        with open('../data/resultats_' + titre + '.csv',
                  'w', encoding = 'utf-8') as fichier:
            writer = csv.writer(fichier, delimiter = ";")
            writer.writerow(['rang','adherent','points'])
            for resultat in Resultat.query.filter(Resultat.id_competition == competition.id).all():
                writer.writerow(resultat.to_csv())
        fichier.close()

def save_connexions():
    with open('../data/connexion.csv', 'w', encoding = 'utf-8') as fichier:
        writer = csv.writer(fichier, delimiter = ";")
        writer.writerow(['adherent','mdp'])
        for escrimeur in Escrimeur.query.all():
            writer.writerow(escrimeur.to_csv()[1])
    fichier.close()

def save_classements():
    for arme in Arme.query.all():
        for categorie in Categorie.query.all():
            for sexe in ('Dames', 'Homme'):
                classements = Classement.query.filter(and_(Classement.arme == arme,
                                                           Classement.categorie == categorie,
                                                           Classement.tireur.has(sexe = sexe))).all()
                nom_arme = arme.libelle
                nom_cat = categorie.libelle
                titre = nom_arme + '_' + sexe + '_' + nom_cat
                with open('../data/classement_' + titre + '.csv',
                          'w', encoding = 'utf-8') as fichier:
                    print(titre)
                    writer = csv.writer(fichier, delimiter = ';')
                    ligne_1 = 'nom;prenom;date naissance;adherent;nation;comite regional;club;points;rang'
                    writer.writerow([col for col in ligne_1.split(';')])
                    for classement in classements:
                        writer.writerow(classement.to_csv())
                fichier.close()
