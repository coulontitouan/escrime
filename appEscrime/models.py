from random import randint
from sqlite3 import IntegrityError

import sqlalchemy
from .app import db, login_manager
from sqlalchemy import *
from flask_login import UserMixin
from datetime import date

TO_DATE = '%d/%m/%Y'

class Lieu(db.Model):
    __tablename__ = 'lieu'
    id = db.Column(db.Integer(), primary_key = True)
    nom = db.Column(db.String(96))
    adresse = db.Column(db.String(96))
    ville = db.Column(db.String(96))
    # Relation un-à-plusieurs : Un lieu peut acceuillir différentes compétitions
    competitions = db.relationship('Competition', back_populates = 'lieu')

    def to_csv(self):
        return [self.nom, self.ville, self.adresse]

class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer(), primary_key = True)
    nom = db.Column(db.String(64))
    region = db.Column(db.String(64))
    # Relation un-à-plusieurs : Un club peut avoir plusieurs adhérents
    adherents = db.relationship('Escrimeur', back_populates = 'club')

    def to_csv(self):
        return [self.region, self.nom]

class Categorie(db.Model):
    __tablename__ = 'categorie'
    id = db.Column(db.Integer(), primary_key = True)
    libelle = db.Column(db.String(32))
    age_maxi = db.Column(db.Integer())
    # Relation un-à-plusieurs : Une catégorie peut définir plusieurs compétitions
    competitions = db.relationship('Competition', back_populates = 'categorie')
    # Relation un-à-plusieurs : Une catégorie peut définir plusieurs classements
    classements = db.relationship('Classement', back_populates = 'categorie')

    def to_csv(self):
        return [self.libelle]

class Arme(db.Model):
    __tablename__ = 'arme'
    id = db.Column(db.Integer(), primary_key = True)
    libelle = db.Column(db.String(32))  
    # Relation un-à-plusieurs : Une arme peut définir plusieurs compétitions
    competitions = db.relationship('Competition', back_populates = 'arme')
    # Relation un-à-plusieurs : Une arme peut définir plusieurs classements
    classements = db.relationship('Classement', back_populates = 'arme')

    def to_csv(self):
        return [self.libelle]

class Escrimeur(db.Model, UserMixin):
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
    authenticated = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):   
        return self.active           

    def is_anonymous(self):
        return False          

    def get_id(self):
        return self.num_licence

    def set_mdp(self, mdp):
        self.mot_de_passe = mdp

    def get_club(self):
        return self.club.nom

    def get_sexe(self):
        return self.sexe

    def is_admin(self):
        return self.id_club == 1

    def to_csv(self):
        naissance = self.date_naissance.strftime(TO_DATE)
        return ([self.nom, self.prenom, naissance, self.num_licence, self.nationalite] + self.club.to_csv(),
                [self.num_licence, self.mot_de_passe])
    def peut_sinscrire(self,id_compet):
        competition = get_competition(id_compet)
        if competition.sexe == self.sexe :
            today = date.today()
            age = today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
            agemax = competition.categorie.age_maxi
            if agemax < 0:
                agemax = 1000
            if age <= agemax and (age <= 39 and "Vétérans" not in competition.categorie.libelle or age > 39 and "Vétérans" in competition.categorie.libelle) :
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

class Classement(db.Model):
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
        return self.tireur.to_csv()[0] + [self.points, self.rang]

class Competition(db.Model):
    __tablename__ = 'competition'
    id = db.Column(db.Integer(), primary_key = True)
    nom = db.Column(db.String(64))
    date = db.Column(db.Date)
    coefficient = db.Column(db.Integer())
    sexe = db.Column(db.String(6))
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

    def nb_phases(self) :
        return len(self.phases)

    def get_tireurs(self):
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id, Resultat.points != -2)

    def get_tireurs_order_by_pts(self):
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id, Resultat.points != -2).order_by(Resultat.points.desc())
    
    def get_tireurs_order_by_rang(self) :
        # participants = self.get_tireurs()
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id, Resultat.points != -2).outerjoin(Classement).filter((Classement.id_arme == self.id_arme) & (Classement.id_categorie == self.id_categorie)).order_by(Classement.rang)

    def get_tireurs_sans_rang(self) :
        liste = self.get_tireurs_order_by_rang()
        liste2 = []
        for x in self.get_tireurs() :
            if x not in liste :
                liste2.append(x)
        return liste2

    def get_arbitres(self):
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id, Resultat.points == -2)

    def get_tireurs_phase(self, id_phase): # PAS BON, IL FAUT DONNER L'ID COMPET ET L'ID PHASE DANS LA REQUETE
        joueurs = set()
        matchs = Match.query.filter_by(id_phase = (self.id,id_phase))
        for m in matchs:
            participations = Participation.query.filter_by(id_match = m.id,
                                                           id_phase = m.id_phase,
                                                           id_competition = m.id_competition)
            for p in participations:
                joueurs.add(Escrimeur.query.get(p.id_escrimeur))
        return joueurs

    def get_arbitres_phase(self, id_phase): # PAS BON, IL FAUT DONNER L'ID COMPET ET L'ID PHASE DANS LA REQUETE
        return Escrimeur.query.get(Match.query.filter_by(id_phase = (self.id,id_phase)).first().num_arbitre)

    def get_points(self, id_tireur):
        return Resultat.query.get((self.id,id_tireur)).points

    def get_categorie(self):
        return self.categorie

    def get_arme(self):
        return self.arme

    def get_lieu(self):
        return self.lieu

    def get_poules(self) :
        res = []
        for phase in self.phases :
            if phase.libelle == 'Poule' :
                res.append(phase)
        return res

    def get_poules_id(self, idp : int) :
        """Récupère une poule en fonction de son ID

        Args:
            idp (int): ID de la poule

        Returns:
            Optional[Phase]: La poule si trouvée, None sinon.
        """
        for phase in self.phases :
            if phase.libelle == 'Poule' and phase.id == idp :
                return phase
        return None

    def inscription(self, num_licence : int, arbitre : bool = False) :
        """Inscrit un tireur à une compétition

        Args:
            num_licence (int): Numéro de licence de l'escrimeur
            arbitre (bool, optional): True si l'escrimeur est arbitre. Defaults to False.
        """
        points = -1
        if arbitre :
            points = -2
        db.session.add(Resultat(id_competition = self.id,
                                id_escrimeur = num_licence,
                                rang = None,
                                points = points))
        db.session.commit()

    def ajoute_poule(self, id_poule):
        db.session.add(Phase(id = id_poule, competition = self, libelle = 'Poule'))

    def programme_poules(self):
        arbitres = self.get_arbitres()
        i = 0
        repartition = self.repartition_poules()
        for poule in self.phases:
            poule.cree_matchs(arbitres[i], repartition[poule.id-1])
            i += 1
        db.session.commit()

    def repartition_poules(self):
        arbitres = self.get_arbitres()
        tireurs = self.get_tireurs()
        nb_arbitres = arbitres.count()
        len_poules = 5
        nb_poules = tireurs.count() // len_poules

        while (nb_poules > nb_arbitres):
            len_poules += 1
            if len_poules == 10:
                return None
            nb_poules = tireurs.count() // len_poules
        
        for i in range(1, nb_poules + 1):
            try:
                self.ajoute_poule(i)
                db.session.commit()
            except(sqlalchemy.exc.IntegrityError):
                db.session.rollback()

        poules = [j for j in range(1, nb_poules + 1)]
        rotation_poules = poules + poules[::-1]
        repartition = []
        for i in range(nb_poules):
            repartition.append([])
        for i in range(tireurs.count()):
            id_poule = rotation_poules[i % len(rotation_poules)]
            repartition[id_poule-1].append(tireurs[i])
        return repartition

    def to_titre_csv(self):
        res = ''
        split = self.nom.split(' ')
        for mot in split:
            res += mot[0].upper() + mot[1:]
        res += '_'
        date_csv = self.date.strftime(TO_DATE)
        for carac in date_csv:
            if carac == '/':
                res += '-'
            else:
                res += carac
        return res + '_' + str(self.id)

    def to_csv(self):
        date_csv = self.date.strftime(TO_DATE)
        return [self.nom, date_csv, self.sexe] + self.categorie.to_csv() + self.arme.to_csv() + [self.coefficient] + self.lieu.to_csv()

    def desinscription(self, num_licence):
        # Vérifier si le participant est inscrit à cette compétition
        resultat = Resultat.query.filter_by(id_competition=self.id, id_escrimeur=num_licence).first()
        if resultat :
            db.session.delete(resultat)
            db.session.commit()
            
    def est_inscrit(self,num_licence):
        user= Resultat.query.filter_by(id_competition = self.id, id_escrimeur = num_licence).first()
        if user == None :
            return False
        else:
            return True
class TypePhase(db.Model):
    __tablename__ = 'type_phase'
    libelle = db.Column(db.String(32), primary_key = True)
    touches_victoire = db.Column(db.Integer())
    # Relation un-à-plusieurs : Un type de phase peut décrire plusieurs phases
    phases = db.relationship('Phase', back_populates = 'type')

class Phase(db.Model):
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

    def nb_tireurs(self) :
        tireurs = set()
        for match in self.matchs :
            for participation in match.participations :
                if participation.id_phase == self.id :
                    tireurs.add(participation.tireur)
        return len(tireurs)
    
    def get_tireurs(self) :
        tireurs = set()
        for match in self.matchs :
            for participation in match.participations :
                if participation.id_phase == self.id :
                    tireurs.add(participation.tireur)
        return tireurs
    
    def get_arbitre(self) :
        return Escrimeur.query.get(self.matchs[0].num_arbitre)

    def cree_matchs(self, arbitre, tireurs):
        liste_matchs = self.programme_matchs_poule(tireurs)
        for i in range(len(liste_matchs)):
            self.ajoute_match(i+1, arbitre, liste_matchs[i][0], liste_matchs[i][1])

    def ajoute_match(self, id_match, arbitre, tireur1, tireur2):
        if self.libelle == 'Poule':
            match = Match(id = id_match,
                          id_competition = self.id_competition,
                          id_phase = self.id,
                          piste = self.id,
                          etat = "A venir",
                          arbitre = arbitre)
            db.session.add(match)
            match.cree_participation(tireur1)
            match.cree_participation(tireur2)
    
    def programme_matchs_poule(self, tireurs):
        nb_journees = len(tireurs) - 1 + (len(tireurs) % 2)
        matchs = set()
        journees = []
        programme = dict()
        for i in range(nb_journees):
            journees.append(set())
        for i in range(len(tireurs)):
            for j in range(i + 1, len(tireurs)):
                matchs.add((tireurs[i], tireurs[j]))

        for match in matchs:
            ok = False
            for j in range(len(journees)):
                if match[0] not in journees[j] and match[1] not in journees[j]:
                    journees[j].add(match[0])
                    journees[j].add(match[1])
                    if j+1 not in programme.keys():
                        programme[j+1] = []
                    programme[j+1].append(match)
                    ok = True
                    break
            if ok == False:
                programme[1].append(match)

        res = []
        for journee in programme.values():
            journee.sort(key=lambda x: x[0].num_licence)
            for match in journee:
                res.append(match)
        return res

    def to_csv(self):
        return [self.id, self.libelle]

class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer())
    # Clé étrangère vers la compétition comprenant le match
    id_competition = db.Column(db.Integer(), db.ForeignKey('competition.id'))
    # Relation plusieurs-à-un unidirectionnel : Un match est compris dans une seule compétition
    competition = db.relationship('Competition')
    # Clé étrangère vers la phase comprenant le match
    id_phase = db.Column(db.Integer(), db.ForeignKey('phase.id'))
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
        {},
    )

    def get_arbitre(self) -> Escrimeur :
        """Récupère l'arbitre associé à ce match.

        Returns:
            Optional[Escrimeur]: L'arbitre du match s'il existe, sinon None.
        """
        return Escrimeur.query.get(self.num_arbitre)

    def cree_participation(self, tireur):
        #print(self.id_competition, self.id_phase, self.id, tireur.num_licence)
        db.session.add(Participation(id_competition = self.id_competition,
                                     id_phase = self.id_phase,
                                     id_match = self.id,
                                     id_escrimeur = tireur.num_licence,
                                     statut = "A venir",
                                     touches = 0))

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

    def to_csv(self):
        return [self.id, self.participations[0], self.participations[1], self.num_arbitre, self.piste, self.etat] + self.phase.to_csv()

class Participation(db.Model):
    __tablename__ = 'participation'
    # Clé étrangère vers la compétition comprenant le match
    id_competition = db.Column(db.Integer(), db.ForeignKey('competition.id'))
    # Relation plusieurs-à-un unidirectionnel : Un match est compris dans une seule compétition
    competition = db.relationship('Competition')
    # Clé étrangère vers la phase comprenant le match
    id_phase = db.Column(db.Integer(), db.ForeignKey('phase.id'))
    # Relation plusieurs-à-un : Un match est compris dans une seule phase de la compétition
    phase = db.relationship('Phase')
    # Clé étrangère vers le match
    id_match = db.Column(db.Integer(), db.ForeignKey('match.id'))
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
        {},
    )

    def get_escrimeur(self) -> Escrimeur :
        """Récupère l'escrimeur associé à cette participation.

        Returns:
            Optional[Escrimeur]: L'escrimeur lié à cette participation, s'il existe.
        """
        return Escrimeur.query.get(self.id_escrimeur)

    def to_csv(self):
        return [self.tireur, self.touches]

class Resultat(db.Model):
    __tablename__ = 'resultat'
    # Clé étrangère vers la compétition
    id_competition = db.Column(db.Integer(), db.ForeignKey('competition.id'))
    # Relation plusieurs-à-un : Un résultat est lié à une seule compétition
    competition = db.relationship('Competition', back_populates = 'resultats')
    # Clé étrangère vers l'escrimeur
    id_escrimeur = db.Column(db.String(16), db.ForeignKey('escrimeur.num_licence'))
    # Relation plusieurs-à-un : Une participation est effectuée par un seul tireur
    escrimeur = db.relationship('Escrimeur', back_populates = 'resultats')
    rang = db.Column(db.Integer())
    points = db.Column(db.Integer())
    __table_args__ = (
        PrimaryKeyConstraint(id_competition, id_escrimeur),
        {},
    )

    def to_csv(self):
        return [self.rang, self.id_escrimeur, self.points]


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

def get_poule(id_competition: int, id_phase: int) -> Phase :
    """Récupère une 'poule' (phase) en fonction de son ID et de l'ID de la compétition.

    Args:
        id_competition (int): L'ID de la compétition.
        id_phase (int): L'ID de la phase.

    Returns:
        Optional[Phase]: La phase (poule) si trouvée, None sinon.
    """
    query = Phase.query.filter_by(id_competition = id_competition, id = id_phase, libelle = 'Poule')
    return query.first()

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

# def get_nb_tireurs_poule(id_poule):
#     poule = get_phase(id_poule)

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

@login_manager.user_loader
def load_user(num_licence):
    return Escrimeur.query.get(num_licence)
