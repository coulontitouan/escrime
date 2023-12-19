"""Module contenant les objets de la base de données."""

import sqlalchemy
from .app import db, login_manager
from sqlalchemy import PrimaryKeyConstraint
from flask_login import UserMixin
from datetime import date

import appEscrime.constants as cst
import requests as rq

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
    _is_authenticated = db.Column(db.Boolean, default=False)
    _is_active = db.Column(db.Boolean, default=False)
    _is_anonymous = db.Column(db.Boolean, default=False)

    @property
    def is_authenticated(self):
        return self._is_authenticated
    @property
    def is_active(self):
        return self._is_active
    @property
    def is_anonymous(self):
        return self._is_anonymous

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
        return ([self.nom,
                 self.prenom,
                 naissance,
                 self.num_licence,
                 self.nationalite]
                 + self.club.to_csv(),
                [self.num_licence,
                 self.mot_de_passe])

    def peut_sinscrire(self, id_compet):
        compet = rq.get_competition(id_compet)
        if compet.sexe == self.sexe:
            today = date.today()
            age = ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
            age = today.year - self.date_naissance.year - age
            agemax = compet.categorie.age_maxi
            if agemax < 0:
                agemax = 1000
            surclassable = age < cst.AGE_MAX_SENIORS and "Vétérans" not in compet.categorie.libelle
            if age < agemax and (surclassable):
                return True
        return False

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

    def get_tireurs(self):
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id,
                                                     Resultat.points != cst.ARBITRE)

    def get_arbitres(self):
        return Escrimeur.query.join(Resultat).filter(Resultat.id_competition == self.id,
                                                     Resultat.points == cst.ARBITRE)

    def get_tireurs_phase(self, id_phase):
        # PAS BON, IL FAUT DONNER L'ID COMPET ET L'ID PHASE DANS LA REQUETE
        joueurs = set()
        matchs = Match.query.filter_by(id_phase = (self.id,id_phase))
        for mmatch in matchs:
            participations = Participation.query.filter_by(id_match = mmatch.id,
                                                           id_phase = mmatch.id_phase,
                                                           id_competition = mmatch.id_competition)
            for participation in participations:
                joueurs.add(Escrimeur.query.get(participation.id_escrimeur))
        return joueurs

    def get_arbitres_phase(self, id_phase):
        # PAS BON, IL FAUT DONNER L'ID COMPET ET L'ID PHASE DANS LA REQUETE
        return Escrimeur.query.get(Match.query.filter_by(id_phase =
                                                         (self.id,id_phase)).first().num_arbitre)

    def get_points(self, id_tireur):
        return Resultat.query.get((self.id,id_tireur)).points

    def get_categorie(self):
        return self.categorie

    def get_arme(self):
        return self.arme

    def get_lieu(self):
        return self.lieu

    def inscription(self, num_licence, arbitre = False):
        points = cst.TIREUR
        if arbitre:
            points = cst.ARBITRE
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
            poule.cree_matchs(arbitres[i], repartition[poule.id - 1])
            i += 1
        db.session.commit()

    def repartition_poules(self):
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
        for j in range(nb_poules):
            poules.append(j+1)
        rotation_poules = poules + poules[::-1]
        repartition = []
        for i in range(nb_poules):
            repartition.append([])
        for i in range(tireurs.count()):
            id_poule = rotation_poules[i % len(rotation_poules)]
            repartition[id_poule-1].append(tireurs[i])
        return repartition

    def desinscription(self, num_licence):
        # Vérifier si le participant est inscrit à cette compétition
        resultat = Resultat.query.filter_by(id_competition=self.id,
                                            id_escrimeur=num_licence).first()
        if resultat:
            db.session.delete(resultat)
            db.session.commit()

    def est_inscrit(self,num_licence):
        user = Resultat.query.filter_by(id_competition = self.id,
                                       id_escrimeur = num_licence).first()
        if user is None :
            return False
        return True

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
        descr = [self.nom, date_csv, self.sexe]
        coef = [self.coefficient]
        return descr + self.categorie.to_csv() + self.arme.to_csv() + coef + self.lieu.to_csv()

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

    def cree_matchs(self, arbitre, tireurs):
        liste_matchs = self.programme_matchs_poule(tireurs)
        for index, match in enumerate(liste_matchs, start=1):
            self.ajoute_match(index, arbitre, match[0], match[1])

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
        programme = {}
        for i in range(nb_journees):
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

    def cree_participation(self, tireur):
        #print(self.id_competition, self.id_phase, self.id, tireur.num_licence)
        db.session.add(Participation(id_competition = self.id_competition,
                                     id_phase = self.id_phase,
                                     id_match = self.id,
                                     id_escrimeur = tireur.num_licence,
                                     statut = "A venir",
                                     touches = 0))

    def to_csv(self):
        return [self.id,
                self.participations[0],
                self.participations[1],
                self.num_arbitre,
                self.piste,
                self.etat] + self.phase.to_csv()

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


@login_manager.user_loader
def load_user(num_licence):
    return Escrimeur.query.get(num_licence)
