"""Module contenant les objets de la base de données."""
# pylint: disable=too-few-public-methods

from datetime import date
import sqlalchemy
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, desc
from flask_login import UserMixin
import appEscrime.constants as cst
from .app import db, login_manager
from collections import defaultdict


class Lieu(db.Model):
    """Classe représentant un lieu acceuillant des compétitions."""
    __tablename__ = 'lieu'
    id = db.Column(db.Integer(), primary_key = True)
    nom = db.Column(db.String(96))
    adresse = db.Column(db.String(96))
    ville = db.Column(db.String(96))
    # Relation un-à-plusieurs : Un lieu peut acceuillir différentes compétitions
    competitions = db.relationship('Competition', back_populates = 'lieu')

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture du lieu dans un fichier csv."""
        return [self.nom, self.ville, self.adresse]

class Club(db.Model):
    """Classe représentant un club d'escrime."""
    __tablename__ = 'club'
    id = db.Column(db.Integer(), primary_key = True)
    nom = db.Column(db.String(64))
    region = db.Column(db.String(64))
    # Relation un-à-plusieurs : Un club peut avoir plusieurs adhérents
    adherents = db.relationship('Escrimeur', back_populates = 'club')

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture du club dans un fichier csv."""
        return [self.region, self.nom]

class Categorie(db.Model):
    """Classe représentant une catégorie d'âge d'escrimeurs."""
    __tablename__ = 'categorie'
    id = db.Column(db.Integer(), primary_key = True)
    libelle = db.Column(db.String(32))
    age_maxi = db.Column(db.Integer())
    # Relation un-à-plusieurs : Une catégorie peut définir plusieurs compétitions
    competitions = db.relationship('Competition', back_populates = 'categorie')
    # Relation un-à-plusieurs : Une catégorie peut définir plusieurs classements
    classements = db.relationship('Classement', back_populates = 'categorie')

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture de la catégorie dans un fichier csv."""
        return [self.libelle]

class Arme(db.Model):
    """Classe représentant une arme d'escrime."""
    __tablename__ = 'arme'
    id = db.Column(db.Integer(), primary_key = True)
    libelle = db.Column(db.String(32))
    # Relation un-à-plusieurs : Une arme peut définir plusieurs compétitions
    competitions = db.relationship('Competition', back_populates = 'arme')
    # Relation un-à-plusieurs : Une arme peut définir plusieurs classements
    classements = db.relationship('Classement', back_populates = 'arme')

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture de l'arme dans un fichier csv."""
        return [self.libelle]

class Escrimeur(db.Model, UserMixin):
    """Classe représentant un escrimeur."""
    __tablename__ = 'escrimeur'
    num_licence = db.Column(db.String(16), primary_key = True)
    prenom = db.Column(db.String(32))
    nom = db.Column(db.String(32))
    sexe = db.Column(db.String(5))
    date_naissance = db.Column(db.Date)
    nationalite = db.Column(db.String(32))
    # Clé étrangère vers le club
    id_club = db.Column(db.Integer(), db.ForeignKey('club.id'))
    # Relation plusieurs-à-un : Un escrimeur est adhérent à un club
    club = db.relationship('Club', back_populates = 'adherents')
    # Relation un-à-plusieurs : Un escrimeur peut être dans différents classements
    classements = db.relationship('Classement', back_populates = 'tireur')
    # Relation un-à-plusieurs : Un escrimeur peut arbitrer différents matchs
    arbitrages = db.relationship('Match', back_populates = 'arbitre')
    # Relation un-à-plusieurs : Un escrimeur peut participer à différents matchs
    participations = db.relationship('Participation', back_populates = 'tireur')
    # Relation un-à-plusieurs : Un escrimeur peut participer à différentes compétitions
    resultats = db.relationship('Resultat', back_populates = 'escrimeur')
    mot_de_passe = db.Column(db.String(64), default = '')

    @property
    def is_authenticated(self) -> bool :
        """Retourne si l'utilisateur est authentifié.

        Returns:
            bool: True si l'utilisateur est authentifié, False sinon.
        """
        return True

    @property
    def is_active(self) -> bool :
        """Retourne si l'utilisateur est actif.

        Returns:
            bool: True si l'utilisateur est actif, False sinon.
        """
        return True

    @property
    def is_anonymous(self) -> bool :
        """Retourne si l'utilisateur est anonyme.

        Returns:
            bool: True si l'utilisateur est anonyme, False sinon.
        """
        return False
    
    def get_id(self):
        """Retourne l'identifiant de l'escrimeur.

        Returns :
            string : l'identifiant de l'escrimeur."""
        return self.num_licence

    def set_mdp(self, mdp):
        """Retourne le mot de passe de l'escrimeur.

        Returns :
            string : le mot de passe de l'escrimeur."""
        self.mot_de_passe = mdp

    def get_club(self):
        """Retourne le nom club de l'escrimeur.

        Returns :
            string : le nom du club de l'escrimeur."""
        return self.club.nom

    def get_sexe(self):
        """Retourne le sexe de l'escrimeur.

        Returns :
            string : le sexe de l'escrimeur."""
        return self.sexe

    def is_admin(self):
        """Retourne si l'utilisateur a le statut administrateur.

        Returns :
            bool : True si l'utilisateur est administrateur, False sinon."""
        return self.id_club == cst.CLUB_ADMIN
    
    def is_arbitre(self,id_compet):
        """Retourne si l'utilisateur est inscrit en tant qu'arbitre.

        Returns :
            bool : True si l'utilisateur est administrateur, False sinon."""
        if self.id_club == cst.CLUB_ADMIN:
            return True
        resultats =  self.resultats
        for resultat in resultats:
            if resultat.id_competition == id_compet and resultat.points == -2:
                return True
        return False
    
    def peut_sinscrire(self, id_compet):
        """Vérifie si l'escrimeur à l'âge requis pour s'inscrie à une compétition donnée.

        Args:
            id_compet (int): l'identifiant de la compétition.

        Returns:
            bool : True si l'escrimeur peut s'inscrire, False sinon.
        """
        compet = Competition.query.get(id_compet)
        if compet.sexe == self.sexe:
            today = date.today()
            age = (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day)
            age = today.year - self.date_naissance.year - age
            agemax = compet.categorie.age_maxi
            if agemax < 0:
                agemax = 1000
            surclassable = age < cst.AGE_MAX_SENIORS and "Vétérans" not in compet.categorie.libelle
            if age < agemax and (surclassable):
                return True
        return False
    

    def get_classement(self, id_arme : int, id_categorie : int) :
        """Récupère le classement d'un tireur pour une arme et une catégorie données.

        Args:
            id_arme (int): ID de l'arme
            id_categorie (int): ID de la catégorie

        Returns:
            Classement: Le classement du tireur pour l'arme et la catégorie données.
        """
        points = Classement.query.get((self.num_licence, id_arme, id_categorie))
        if points is None :
            points = Classement(rang = 0,
                                points = 0,
                                num_licence = self.num_licence,
                                id_arme = 0,
                                id_categorie = 0)
        return points
    
    def get_id_match(self, id_compet, id_phase):
        """Récupère l'id du match d'un escrimeur dans une phase donnée

        Args:
            id_compet (int): l'identifiant de la compétition contenant la phase
            id_phase (int): l'identifiant de la phase

        Returns:
            int: l'identifiant du match de l'escrimeur dans la phase donnée
        """
        return (Participation.query.filter(Participation.id_competition == id_compet,
                                          Participation.id_phase == id_phase,
                                          Participation.id_escrimeur == self.num_licence)
                                          .first().id_match)
    
    def get_historique_resultat(self):
        return (Resultat.query.join(Competition).filter(Resultat.id_escrimeur == self.num_licence).order_by(Competition.date.desc()).all())

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture de l'escrimeur dans un fichier csv."""
        naissance = self.date_naissance.strftime(cst.TO_DATE)
        return ([self.nom,
                 self.prenom,
                 naissance,
                 self.num_licence,
                 self.nationalite]
                 + self.club.to_csv(),
                 [self.num_licence,
                 self.mot_de_passe])

class Classement(db.Model):
    """Classe représentant un classement d'un escrimeur dans une catégorie avec une arme."""
    __tablename__ = 'classement'
    rang = db.Column(db.Integer())
    points = db.Column(db.Integer())
    # Clé étrangère vers le tireur
    num_licence = db.Column(db.String(16), db.ForeignKey('escrimeur.num_licence'))
    # Relation plusieurs-à-un : Un classement est lié à un seul tireur
    tireur = db.relationship('Escrimeur', back_populates = 'classements')
    # Clé étrangère vers l'arme
    id_arme = db.Column(db.Integer(), db.ForeignKey('arme.id'))
    # Relation plusieurs-à-un : Un classement est définis par une seule arme
    arme = db.relationship('Arme', back_populates = 'classements')
    # Clé étrangère vers la catégorie
    id_categorie = db.Column(db.Integer(), db.ForeignKey('categorie.id'))
    # Relation plusieurs-à-un : Un classement est définis par une seule catégorie
    categorie = db.relationship('Categorie', back_populates = 'classements')
    __table_args__ = (
        PrimaryKeyConstraint(num_licence, id_arme, id_categorie),
        {},
    )

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture du classement dans un fichier csv."""
        return self.tireur.to_csv()[0] + [self.points, self.rang]

class Competition(db.Model):
    """Classe représentant une compétition d'escrime."""
    __tablename__ = 'competition'
    id = db.Column(db.Integer(), primary_key = True)
    nom = db.Column(db.String(64))
    date = db.Column(db.Date)
    coefficient = db.Column(db.Integer())
    sexe = db.Column(db.String(6))
    est_individuelle = db.Column(db.Boolean, default=True)
    # Clé étrangère vers le lieu
    id_lieu = db.Column(db.Integer(), db.ForeignKey('lieu.id'))
    # Relation plusieurs-à-un : Une compétition se déroule dans un seul lieu
    lieu = db.relationship('Lieu', back_populates = 'competitions')
    # Clé étrangère vers l'arme
    id_arme = db.Column(db.Integer(), db.ForeignKey('arme.id'))
    # Relation plusieurs-à-un : Un classement est définis par une seule arme
    arme = db.relationship('Arme', back_populates = 'competitions')
    # Clé étrangère vers la catégorie
    id_categorie = db.Column(db.Integer(), db.ForeignKey('categorie.id'))
    # Relation plusieurs-à-un : Un classement est définis par une seule catégorie
    categorie = db.relationship('Categorie', back_populates = 'competitions')
    # Relation un-à-plusieurs : Une compétition contient différentes phases
    phases = db.relationship('Phase', back_populates = 'competition')
    # Relation un-à-plusieurs : Une compétition comprend plusieurs escrimeurs
    resultats = db.relationship('Resultat', back_populates = 'competition')

    def get_categorie(self):
        """Retourne la catégorie de la compétition.

        Returns:
            Categorie: la catégorie de la compétition.
        """
        return self.categorie

    def get_arme(self):
        """Retourne l'arme de la compétition.

        Returns:
            Arme: l'arme de la compétition.
        """
        return self.arme

    def get_lieu(self):
        """Retourne le lieu de la compétition.

        Returns:
            Lieu: le lieu de la compétition.
        """
        return self.lieu
    
    def nb_phases(self):
        """Retourne le nombre de phases de la compétition.

        Returns:
            int: le nombre de phases de la compétition.
        """
        return len(self.phases)
    
    def nb_phases_finales(self):
        """Retourne le nombre de phases finales de la compétition.

        Returns:
            int: le nombre de phases finales de la compétition.
        """
        res = [phase for phase in self.phases if phase.libelle != 'Poule']
        return len(res)

    def nb_poules(self):
        """Retourne le nombre de poules de la compétition.

        Returns:
            int: le nombre de poules de la compétition.
        """
        res = [phase for phase in self.phases if phase.libelle == 'Poule']
        return len(res)

    def get_tireurs(self):
        """Retourne les tireurs inscrits à la compétition.

        Returns:
            Query: le résultat de la requête des tireurs inscrits à la compétition.
        """
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id,
                                                        Resultat.points != cst.ARBITRE)
    
    def get_nb_tireurs(self):
        """Retourne le nombre de tireurs inscrits à la compétition.

        Returns:
            Query: le résultat de la requête du nombre de tireurs inscrits à la compétition.
        """
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id,
                                                        Resultat.points != cst.ARBITRE).count()

    def get_tireurs_order_by_pts(self) :
        """Retourne les tireurs inscrits à la compétition, triés par points.

        Returns:
            Query: le résultat de la requête des tireurs inscrits à la compétition.
        """
        query_tireur = Escrimeur.query.join(Resultat)
        query_tireur_filtre = query_tireur.filter(Resultat.id_competition == self.id,
                                                    Resultat.points != -2)
        return query_tireur_filtre.order_by(Resultat.points.desc())

    def get_tireurs_order_by_rang(self) :
        """Retourne les tireurs inscrits à la compétition, triés par rang.

        Returns:
            Query: le résultat de la requête des tireurs inscrits à la compétition.
        """
        query_join = Escrimeur.query.join(Resultat)
        query_filtre = query_join.filter(Resultat.id_competition == self.id, Resultat.points != -2)
        query_outer = query_filtre.outerjoin(Classement)
        condition = Classement.id_arme == self.id_arme
        condition2 = Classement.id_categorie == self.id_categorie
        query_filtre2 = query_outer.filter(condition & condition2)
        return query_filtre2.order_by(Classement.rang)

    def get_tireurs_sans_rang(self) -> list :
        """Retourne les tireurs inscrits à la compétition, sans rang.

        Returns:
            Query: le résultat de la requête des tireurs inscrits à la compétition.
        """
        liste = self.get_tireurs_order_by_rang()
        liste2 = []
        for tireur in self.get_tireurs() :
            if tireur not in liste :
                liste2.append(tireur)
        return liste2
    
    def get_arbitres(self):
        """Retourne les arbitres inscrits à la compétition.

        Returns:
            Query: le résultat de la requête des arbitres inscrits à la compétition.
        """
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id,
                                                     Resultat.points == cst.ARBITRE)
    
    def get_points(self, id_tireur):
        """Retourne les points d'un tireur à la compétition.

        Args:
            id_tireur (string): l'identifiant du tireur.

        Returns:
            int: les points inscrits par le tireur à la compétition."""
        return Resultat.query.get((self.id,id_tireur)).points
    
    def get_phases_tableau(self) -> list :
        """Récupère les phases du tableau de la compétition

        Returns:
            list[Phase]: Les phases du tableau de la compétition
        """
        res = []
        for phase in self.phases :
            if phase.libelle != 'Poule' :
                res.append(phase)
        return sorted(res, key=lambda phase: phase.id, reverse=True)
    
    def get_poules(self) -> list :
        """Récupère les poules de la compétition

        Returns:
            list[Phase]: Les poules de la compétition
        """
        res = []
        for phase in self.phases :
            if phase.libelle == 'Poule' :
                res.append(phase)
        return res

    def get_phases_id(self, idp : int) :
        """Récupère une poule en fonction de son ID

        Args:
            idp (int): ID de la poule

        Returns:
            Optional[Phase]: La poule si trouvée, None sinon.
        """
        for phase in self.phases :
            if phase.id == idp :
                return phase
        return None
    
    def inscription(self, num_licence : int, arbitre : bool = False, id_groupe : int = cst.COMPET_INDIV, est_chef : bool = False) :
        """Inscrit un tireur à une compétition

        Args:
            num_licence (int): Numéro de licence de l'escrimeur
            arbitre (bool, optional): True si l'escrimeur est arbitre. Defaults to False.
        """
        points = cst.TIREUR
        if arbitre :
            points = cst.ARBITRE
        db.session.add(Resultat(id_competition = self.id,
                                id_escrimeur = num_licence,
                                rang = None,
                                points = points,est_chef = est_chef,id_groupe = id_groupe))
        db.session.commit()

    def inscription_groupe(self,num_licence_chef,groupe:tuple,):
        id_groupe = Resultat.query.filter_by(id_competition = self.id).order_by(desc(Resultat.id_groupe)).first().id_groupe1+1
        for num_licence in groupe:
            self.inscription(numlicence = num_licence,id_groupe = id_groupe)
        self.inscription(numlicence = num_licence_chef,id_groupe = id_groupe, est_chef= True)

    def ajoute_poule(self, id_poule):
        """Ajoute une poule à la compétition.

        Args:
            id_poule (int): l'identifiant de la poule au sein de la compétition
        """
        db.session.add(Phase(id = id_poule, competition = self, libelle = 'Poule'))

    def repartition_poules(self):
        """Répartit les tireurs inscrits à la compétition dans les poules.

        Returns:
            list: une liste de liste de tireurs, chaque liste correspondant à une poule.
        """
        arbitres = self.get_arbitres()
        tireurs = self.get_tireurs()
        nb_arbitres = arbitres.count()
        len_poules = 5
        nb_poules = tireurs.count() // len_poules

        while nb_poules > nb_arbitres:
            len_poules += 1
            if len_poules == 10:
                return None
            nb_poules = tireurs.count() // len_poules
        for i in range(1, nb_poules + 1):
            try:
                self.ajoute_poule(i)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()

        poules = []
        for j in range(len(self.phases)):
            poules.append(j+1)
        rotation_poules = poules + poules[::-1]
        repartition = []
        for i in range(len(self.phases)):
            repartition.append([])
        for i in range(tireurs.count()):
            id_poule = rotation_poules[i % len(rotation_poules)]
            repartition[id_poule-1].append(tireurs[i])
        return repartition

    def programme_poules(self):
        """Crée les matchs des poules de la compétition."""
        arbitres = list(self.get_arbitres())
        repartition = self.repartition_poules()
        for poule in self.phases:
            poule.cree_matchs(arbitres, repartition[poule.id - 1])
        db.session.commit()

    def ajoute_tour_tableau(self, libelle):
        """Ajoute un tour de tableau à la compétition.

        Args:
            libelle (string): le libellé du tour de tableau.
        """
        try:
            db.session.add(TypePhase(libelle = libelle,
                                     touches_victoire = cst.TOUCHES_BRACKET))
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
        db.session.add(Phase(id = len(self.phases) + 1,
                             competition = self,
                             libelle = libelle))
        db.session.commit()
    
    def reduction_tableau(self, tireurs):
        """Réduit si nécessaire le nombre de tireurs participant à un tour du tableau.

        Args:
            tireurs (list): la liste des licences des tireurs encore en lice.

        Returns:
            list: la liste des tireurs participant au prochain tour.
        """
        nb_tireurs = len(tireurs)
        puissance_proche = puissance_de_deux_proches(nb_tireurs)
        nb_matchs = (nb_tireurs - puissance_proche)
        tireurs = tireurs[-nb_matchs*2:]
        return tireurs
    
    def programme_tableau(self):
        """Crée les matchs du tableau de la compétition."""
        if self.est_tour_termine():
            arbitres = self.get_arbitres()
            self.maj_resultat()
            en_lice = Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id,
                                                            Resultat.rang == "",
                                                            Resultat.points != cst.ARBITRE).all()
            tireurs = [res for res in en_lice]
            if len(tireurs) == 2:
                tour = "Finale"
            elif len(tireurs) == 4:
                tour = "Demi-finale"
            elif len(tireurs) == 8:
                tour = "Quarts de finale"
            else:
                tour = str(int(len(tireurs)/2)) + "èmes de finale"

            if bin(len(tireurs)).count("1") > 1:
                tireurs = self.reduction_tableau(tireurs)
                tour = "Barrages"
            self.ajoute_tour_tableau(tour)
            phase = self.phases[-1]
            phase.cree_matchs(list(arbitres), tireurs)
            db.session.commit()
        else:
            print("\nLe tour précédent n'est pas terminé\n")

    def maj_resultat(self):
        """Met à jour le résultat de la compétition."""
        classement = self.get_tireurs_classes()
        pos = len(Resultat.query.filter_by(id_competition = self.id,
                                           rang = "",
                                           points = cst.TIREUR).all())
        if self.phases[-1].libelle != "Poule": # Si on au moins au premier tour du tableau
            for licence in classement.keys():
                print("maj_resultat", self.id, self.phases[-1].id, licence, pos)
                try:
                    if Participation.query.filter_by(id_competition=self.id,
                                                     id_phase=self.phases[-1].id,
                                                     id_escrimeur=licence).first().statut == cst.PERDANT:
                        Resultat.query.get((self.id, licence)).rang = pos
                except AttributeError:
                    print("Skip", licence)
    
    def est_tour_termine(self):
        """Vérifie si le dernier tour de la compétition est terminé."""
        if self.phases[-1].libelle == "Poule":
            for poule in self.phases:
                if not poule.est_terminee():
                    return False
        else:
            if not self.phases[-1].est_terminee():
                return False
        return True

    def desinscription(self, num_licence):
        """Désinscrit un escrimeur de la compétition.

        Args:
            num_licence (string): l'identifiant de l'escrimeur.
        """
        # Vérifier si le participant est inscrit à cette compétition
        resultat = Resultat.query.filter_by(id_competition=self.id,
                                            id_escrimeur=num_licence).first()
        if resultat:
            db.session.delete(resultat)
            db.session.commit()

    def est_inscrit(self,num_licence):
        """Vérifie si un escrimeur est inscrit à la compétition.

        Args:
            num_licence (string): l'identifiant de l'escrimeur.

        Returns:
            bool: True si l'escrimeur est inscrit, False sinon.
        """
        user = Resultat.query.filter_by(id_competition = self.id,
                                        id_escrimeur=num_licence).first()
        if user is None :
            return False
        return True

    def dico_victoire_tireur(self):
        """renvoie le dictionnaire des performances de la competition, non trié
        dico[num_licence]["victoires"]
                         ["matchs"]
                         ["touches"]
        Returns:
            dict: dico[num_licence][str]
        """
        dico = defaultdict(lambda: defaultdict(int))
        traites = set()
        for participant1 in Participation.query.filter_by(id_competition = self.id).all():
            if (participant1.id_phase,participant1.id_match) not in traites:
                participants = (Participation.query
                                .filter_by(id_competition = self.id,
                                           id_match = participant1.id_match,
                                           id_phase = participant1.id_phase)
                                .all())
                participant2 = [participant for participant in participants
                                if participant.id_escrimeur != participant1.id_escrimeur][0]

                traites.add((participant1.id_phase, participant1.id_match))
                if (participant1.statut != cst.MATCH_A_VENIR):
                    dico[max([participant1, participant2], key=lambda p: p.touches).id_escrimeur]["victoires"]+=1
                    for participant in [participant1,participant2]:
                        dico[participant.id_escrimeur]["touches"]+=participant.touches
                        dico[participant.id_escrimeur]["matchs"]+=1

        for resultat in Resultat.query.filter_by(id_competition = self.id).all():
            if resultat.rang != "" and resultat.points != cst.ARBITRE:
                dico[resultat.id_escrimeur]["rang"] = -resultat.rang
        return dico
    
    def dico_victoire_tireur_poule(self):
        """renvoie le dictionnaire des performances de la competition, non trié
        dico[num_licence]["victoires"]
                         ["matchs"]
                         ["touches"]
        Returns:
            dict: dico[num_licence][str]
        """
        dico = defaultdict(lambda: defaultdict(int))
        traites = set()
        for phase in Phase.query.filter_by(id_competition = self.id).all():
            if phase.libelle == "Poule":
                for participant1 in Participation.query.filter_by(id_competition = self.id,id_phase = phase.id).all():
                    if (participant1.id_phase,participant1.id_match) not in traites:
                        participants = (Participation.query
                                        .filter_by(id_competition = self.id,
                                                id_match = participant1.id_match,
                                                id_phase = participant1.id_phase)
                                        .all())
                        participant2 = [participant for participant in participants
                                        if participant.id_escrimeur != participant1.id_escrimeur][0]

                        traites.add((participant1.id_phase, participant1.id_match))
                        if (participant1.statut != cst.MATCH_A_VENIR):
                            dico[max([participant1, participant2], key=lambda p: p.touches).id_escrimeur]["victoires"]+=1
                            for participant in [participant1,participant2]:
                                dico[participant.id_escrimeur]["touches"]+=participant.touches
                                dico[participant.id_escrimeur]["matchs"]+=1
                        
                        else:
                            for participant in [participant1,participant2]:
                                if dico[participant.id_escrimeur]["matchs"] == 0:
                                    dico[participant.id_escrimeur]["victoires"]=0
                                    dico[participant.id_escrimeur]["touches"] = 0
                                    dico[participant.id_escrimeur]["matchs"]+=1


        return dico
    
    def get_tireurs_classes(self):
        """renvoie le dictionnaire des performances de la competition 
        trié par ratio victoires/matchs et ensuite par touches si égalité

        Returns:
            _type_: dico[num_licence][str]
        """
        dico = self.dico_victoire_tireur()
        def cle_tri(cle):
            return (
                dico[cle]["rang"],
                dico[cle]["victoires"] / dico[cle]["matchs"],  
                dico[cle]["touches"] 
            )
        dico_trie = dict(sorted(dico.items(), key=lambda x: cle_tri(x[0]), reverse=True))
        return dico_trie
    
    def get_tireurs_classes_poule(self):
        """renvoie le dictionnaire des performances de la competition 
        trié par ratio victoires/matchs et ensuite par touches si égalité

        Returns:
            _type_: dico[num_licence][str]
        """
        dico = self.dico_victoire_tireur_poule()
        def cle_tri(cle):
            return (
                dico[cle]["victoires"] / dico[cle]["matchs"],  
                dico[cle]["touches"] 
            )
        dico_trie = dict(sorted(dico.items(), key=lambda x: cle_tri(x[0]), reverse=True))
        return dico_trie
    
    def peux_genere_phase_suivante(self) :
        for phase in self.phases :
            for match in phase.matchs :
                if match.etat != cst.MATCH_TERMINE or Phase.query.filter_by(id_competition = self.id).order_by(Phase.id.desc()).first().libelle == "Finale":
                    return False
        return True

    def to_titre_csv(self):
        """Retourne le format du titre du fichier csv de la compétition."""
        res = ''
        split = self.nom.split(' ')
        for mot in split:
            res += mot[0].upper() + mot[1:]
        res += '_'
        date_csv = self.date.strftime(cst.TO_DATE)
        for carac in date_csv:
            if carac == '/':
                res += '-'
            else:
                res += carac
        return res + '_' + str(self.id)

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture de la compétition dans un fichier csv."""
        date_csv = self.date.strftime(cst.TO_DATE)
        descr = [self.nom, date_csv, self.sexe]
        coef = [self.coefficient]
        return descr + self.categorie.to_csv() + self.arme.to_csv() + coef + self.lieu.to_csv()

class TypePhase(db.Model):
    """Classe représentant un type de phase d'une compétition."""
    __tablename__ = 'type_phase'
    libelle = db.Column(db.String(32), primary_key = True)
    touches_victoire = db.Column(db.Integer())
    # Relation un-à-plusieurs : Un type de phase peut décrire plusieurs phases
    phases = db.relationship('Phase', back_populates = 'type')

class Phase(db.Model):
    """Classe représentant une phase d'une compétition."""
    __tablename__ = 'phase'
    id = db.Column(db.Integer())
    # Clé étrangère vers la compétition comprenant la phase
    id_competition = db.Column(db.Integer(), db.ForeignKey('competition.id'))
    # Relation plusieurs-à-un : Une phase est comprise dans une seule compétition
    competition = db.relationship('Competition', back_populates = 'phases')
    # Clé étrangère vers le type de phase
    libelle = db.Column(db.String(32), db.ForeignKey('type_phase.libelle'))
    # Relation plusieurs-à-un : Une phase est décrite par un seul type de phase
    type = db.relationship('TypePhase', back_populates = 'phases')
    # Relation un-à-plusieurs : Une compétition contient différentes phases
    matchs = db.relationship('Match', back_populates = 'phase')
    __table_args__ = (
        PrimaryKeyConstraint(id, id_competition),
        {},
    )

    def nb_tireurs(self) -> int :
        """Retourne le nombre de tireurs de la phase.

        Returns:
            int: le nombre de tireurs de la phase.
        """
        tireurs = set()
        for match in self.matchs :
            for participation in match.participations :
                if participation.id_phase == self.id :
                    tireurs.add(participation.tireur)
        return len(tireurs)

    def get_tireurs(self) :
        return Escrimeur.query.join(Participation).filter(Participation.id_competition == self.id_competition, Participation.id_phase == self.id).order_by(Participation.id_match)

    def get_arbitre(self) -> Escrimeur :
        """Récupère l'arbitre de la phase.

        Returns:
            Escrimeur: l'arbitre de la phase.
        """
        return Escrimeur.query.get(self.matchs[0].num_arbitre)

    def cree_matchs(self, arbitres, tireurs):
        """Crée les matchs de la phase.

        Args:
            arbitres (list): la liste des arbitres de la phase.
            tireurs (list): la liste des tireurs de la phase.
        """
        if self.libelle == 'Poule':
            liste_matchs = self.programme_matchs_poule(tireurs)
            for index, match in enumerate(liste_matchs, start=1):
                self.ajoute_match(index,
                                  arbitres[0],
                                  match[0],
                                  match[1])
        else:
            for i in range(len(tireurs)//2):
                self.ajoute_match(i+1,
                                  arbitres[i % len(arbitres)],
                                  tireurs[i],
                                  tireurs[-i-1])

    def ajoute_match(self, id_match, arbitre, tireur1, tireur2):
        """Ajoute un match à la phase.

        Args:
            id_match (int): l'identifiant du match au sein de la phase.
            arbitre (Escrimeur): l'arbitre du match
            tireur1 (Escrimeur): le premier tireur du match
            tireur2 (Escrimeur): le second tireur du match
        """
        match = Match(id = id_match,
                      id_competition = self.id_competition,
                      id_phase = self.id,
                      piste = self.id,
                      etat = cst.MATCH_A_VENIR,
                      arbitre = arbitre)
        match.cree_participation(tireur1)
        match.cree_participation(tireur2)
        db.session.add(match)

    def programme_matchs_poule(self, tireurs):
        """Organise l'ordre des matchs de la phase.

        Args:
            tireurs (list): la liste des tireurs de la phase.
        """
        nb_journees = len(tireurs) - 1 + (len(tireurs) % 2)
        journees = []
        programme = {}
        for _ in range(nb_journees):
            journees.append(set())
        matchs = [(tireurs[i], tireurs[j])
                    for i in range(len(tireurs))
                    for j in range(i + 1, len(tireurs))]

        for match in matchs:
            insere = False
            for j, journee in enumerate(journees, start=1):
                if match[0] not in journee and match[1] not in journee:
                    journee.add(match[0])
                    journee.add(match[1])
                    programme.setdefault(j, []).append(match)
                    insere = True
                    break
            if insere is False:
                programme[1].append(match)

        res = []
        for journee in programme.values():
            journee.sort(key=lambda x: x[0].get_id())
            for match in journee:
                res.append(match)
        return res
     
    def get_match_id(self, id_match : int):
        """Récupère un match en fonction de son ID dans une poule

        Args:
            id_match (int): ID du match

        Returns:
            Match: Le match.
        """
        return Match.query.get((id_match, self.id, self.id_competition))
    
    def get_vainqueurs(self):
        """Récupère les vainqueurs de la phase.

        Returns:
            List[Participation]: Les participations des vainqueurs de la phase.
        """
        res = []
        for match in self.matchs :
            for participation in match.participations :
                if participation.statut == cst.VAINQUEUR :
                    res.append(participation)
        return res

    def get_perdants(self):
        """Récupère les perdants de la phase.

        Returns:
            List[Participation]: Les participations des perdants de la phase.
        """
        res = []
        for match in self.matchs :
            for participation in match.participations :
                if participation.statut == cst.PERDANT :
                    res.append(participation)
        return res
    
    def est_terminee(self) -> bool :
        """Vérifie que la phase est terminée.

        Returns:
            bool: True si la phase est terminée, False sinon.
        """
        for match in self.matchs :
            if match.etat != cst.MATCH_TERMINE :
                return False
        return True
    
    def verrouille_resultats(self):
        """Valide les résultats de la phase et gère la création de la suivante."""
        if self.est_terminee() and self.libelle != 'Finale' and self.libelle != 'Poule':
            self.competition.programme_tableau()
    
    def get_matchs_tireur(self, id_tireur : int) :
        """Récupère les matchs d'un tireur dans la phase

        Args:
            id_tireur (int): ID du tireur

        Returns:
            List[Match]: Les matchs du tireur.
        """
        return sorted(
            [match for match in self.matchs if id_tireur in [participation.id_escrimeur for participation in match.participations]],
            key=lambda match: [participation.id_escrimeur for participation in match.participations if participation.id_escrimeur != id_tireur][0])
        
    
    def get_total_touches_recues_tireur(self, id_tireur : int) :
        """Récupère le total des touches reçues par un tireur dans la phase.

        Args:
            id_tireur (int): ID du tireur

        Returns:
            int: Le total des touches reçues par le tireur.
        """
        return sum([[
            participation.touches for participation in couple_participation
                     if participation.id_escrimeur != id_tireur][0] 
                    for couple_participation in [
                        match.participations for match in self.get_matchs_tireur(id_tireur)]])
    
    def get_total_touches_realisees_tireur(self, id_tireur : int) :
        """Récupère le total des touches réalisées par un tireur dans la phase.

        Args:
            id_tireur (int): ID du tireur

        Returns:
            int: Le total des touches réalisées par le tireur.
        """
        return sum([[participation.touches for participation in couple_participation if participation.id_escrimeur == id_tireur][0] for couple_participation in [match.participations for match in self.get_matchs_tireur(id_tireur)]])

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture de la phase dans un fichier csv."""
        return [self.id, self.libelle]

class Match(db.Model):
    """Classe représentant un match d'une compétition."""
    __tablename__ = 'match'
    id = db.Column(db.Integer())
    # Clé étrangère vers la compétition comprenant le match
    id_competition = db.Column(db.Integer(), nullable=False)
    # Clé étrangère vers la phase comprenant le match
    id_phase = db.Column(db.Integer(), nullable=False)
    # Relation plusieurs-à-un : Un match est compris dans une seule phase de la compétition
    phase = db.relationship('Phase', back_populates = 'matchs')
    piste = db.Column(db.Integer())
    etat = db.Column(db.String(16))
    # Clé étrangère vers l'arbitre escrimeur
    num_arbitre = db.Column(db.String(16), db.ForeignKey('escrimeur.num_licence'))
    # Relation plusieurs-à-un : Un match est arbitré par un seul arbitre
    arbitre = db.relationship('Escrimeur', back_populates = 'arbitrages')
    # Relation un-à-plusieurs : Un match est arbitré par un seul arbitre
    participations = db.relationship('Participation', back_populates = 'match')
    __table_args__ = (
        PrimaryKeyConstraint(id, id_phase, id_competition),
        ForeignKeyConstraint([id_competition, id_phase], [Phase.id_competition, Phase.id]),
        {},
    )
    
    def get_arbitre(self) -> Escrimeur :
        """Récupère l'arbitre associé à ce match.

        Returns:
            Optional[Escrimeur]: L'arbitre du match s'il existe, sinon None.
        """
        return Escrimeur.query.get(self.num_arbitre)
    
    def get_participation(self, id_tireur) :
        """Récupère la participations d'un tireur dans le match.

        Args:
            id_tireur (int): ID du tireur

        Returns:
            Participation: La participation du tireur dans le match.
        """
        return [participation for participation in self.participations if participation.id_escrimeur == id_tireur][0]

    def set_en_cours(self):
        """Met le match en cours."""
        self.etat = cst.MATCH_EN_COURS
        db.session.commit()

    def cree_participation(self, tireur):
        """Crée les participations des tireurs au match.

        Args:
            tireur (Escrimeur): un escrimeur participant au match.
        """
        db.session.add(Participation(id_competition = self.id_competition,
                                     id_phase = self.id_phase,
                                     id_match = self.id,
                                     id_escrimeur = tireur.num_licence,
                                     statut = cst.MATCH_A_VENIR,
                                     touches = 0))
    
    def valide_resultat(self, vainqueur, perdant):
        """Valide le résultat d'un match.

        Args:
            vainqueur (tuple):
                un tuple contenant le numéro de licence et le nombre de touches du vainqueur.
            perdant (tuple):
                un tuple contenant le numéro de licence et le nombre de touches du perdant.
        """
        num_vainqueur, touches_vainqueur = vainqueur[0], vainqueur[1]
        num_perdant, touches_perdant = perdant[0], perdant[1]
        for participation in self.participations:
            if participation.id_escrimeur == num_vainqueur:
                participation.statut = cst.VAINQUEUR
                participation.touches = touches_vainqueur
            elif participation.id_escrimeur == num_perdant:
                participation.statut = cst.PERDANT
                participation.touches = touches_perdant
            else:
                print("Tireur inconnu wtf ?!")
        self.etat = cst.MATCH_TERMINE
        db.session.commit()

    def get_tireurs_match(self, id_poule : int) :
        """Récupère les tireurs d'un match en fonction de l'ID de la poule.

        Args:
            id_poule (int): ID de la poule

        Returns:
            List[Participation]: Les participations des tireurs du match.
        """
        participants = []
        for participation in self.participations:
            if participation.id_phase == id_poule :
                participants.append(participation)
        return participants
    
    def get_gagnant(self) :
        """Récupère le vainqueur du match.

        Returns:
            Optional[str]: Le numéro de licence du vainqueur, s'il existe.
        """
        for participation in self.participations:
            if participation.statut == cst.VAINQUEUR :
                return participation.id_escrimeur
        return None

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture du match dans un fichier csv."""
        return [self.id,
                self.participations[0],
                self.participations[1],
                self.num_arbitre,
                self.piste,
                self.etat] + self.phase.to_csv()

class Participation(db.Model):
    """Classe représentant une participation d'un escrimeur à un match d'une compétition."""
    __tablename__ = 'participation'
    # Clé étrangère vers la compétition comprenant le match
    id_competition = db.Column(db.Integer(), nullable=False)
    # Clé étrangère vers la phase comprenant le match
    id_phase = db.Column(db.Integer(), nullable=False)
    # Clé étrangère vers le match
    id_match = db.Column(db.Integer(), nullable=False)
    # Relation plusieurs-à-un : Une participation est liée à un seul match
    match = db.relationship('Match', back_populates = 'participations')
    # Clé étrangère vers le tireur
    id_escrimeur = db.Column(db.String(16), db.ForeignKey('escrimeur.num_licence'))
    # Relation plusieurs-à-un : Une participation est effectuée par un seul tireur
    tireur = db.relationship('Escrimeur', back_populates = 'participations')
    statut = db.Column(db.String(16))
    touches = db.Column(db.Integer())
    __table_args__ = (
        PrimaryKeyConstraint(id_competition, id_phase, id_match, id_escrimeur),
        ForeignKeyConstraint([id_competition, id_phase, id_match],
                            [Match.id_competition, Match.id_phase, Match.id]),
        {},
    )

    def get_escrimeur(self) -> Escrimeur :
        """Récupère l'escrimeur associé à cette participation.

        Returns:
            Optional[Escrimeur]: L'escrimeur lié à cette participation, s'il existe.
        """
        return Escrimeur.query.get(self.id_escrimeur)

    def to_csv(self):
        """Retourne les données nécessaires à l'écriture de la participation dans un fichier csv."""
        return [self.tireur, self.touches]

class Resultat(db.Model):
    """Classe représentant le résultat final d'un escrimeur à une compétition."""
    __tablename__ = 'resultat'
    # Clé étrangère vers la compétition
    id_competition = db.Column(db.Integer(), db.ForeignKey('competition.id'))
    # Relation plusieurs-à-un : Un résultat est lié à une seule compétition
    competition = db.relationship('Competition', back_populates = 'resultats')
    # Clé étrangère vers l'escrimeur
    id_escrimeur = db.Column(db.String(16), db.ForeignKey('escrimeur.num_licence'))
    # Relation plusieurs-à-un : Une participation est effectuée par un seul tireur
    escrimeur = db.relationship('Escrimeur', back_populates = 'resultats')
    id_groupe = db.Column(db.Integer(),default = cst.COMPET_INDIV)
    est_chef = db.Column(db.Boolean, default = False)
    rang = db.Column(db.Integer())
    points = db.Column(db.Integer())
    __table_args__ = (
        PrimaryKeyConstraint(id_competition, id_escrimeur),
        {},
    )
    def to_csv(self):
        """Retourne les données nécessaires à l'écriture du résultat dans un fichier csv."""
        return [self.rang, self.id_escrimeur, self.points]


@login_manager.user_loader
def load_user(num_licence : str) -> Escrimeur :
    """-----------OBLIGATOIRE-----------
        Fonction qui permet de récupérer un escrimeur dans la base de données

    Args:
        num_licence (string): le numéro de licence d'un escrimeur

    Returns:
        Escrimeur: l'escrimeur correspondant au numéro de licence
    """
    return Escrimeur.query.get(num_licence)


def puissance_de_deux_proches(n):
    """Calcule la puissance de deux la plus proche d'un nombre donné

    Args:
        n (int): un nombre entier positif

    Returns:
        int: la puissance de deux la plus proche de n
    """
    position_bit_significatif = 0
    temp_n = n
    while temp_n > 0:
        temp_n >>= 1
        position_bit_significatif += 1
    puissance_inferieure = 1 if n == 0 else 1 << (position_bit_significatif - 1)
    return puissance_inferieure
