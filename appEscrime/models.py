from .app import db, login_manager
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin

Base = declarative_base()

Inscription = db.Table('inscriptions', Base.metadata,
                       db.Column('num_escrimeur', db.Integer, db.ForeignKey('escrimeur.num_licence')),
                       db.Column('id_compet', db.Integer, db.ForeignKey('competition.id'))
                       )

class Lieu(db.Model):
    __tablename__ = 'lieu'
    id = db.Column(db.Integer, primary_key = True)
    nom = db.Column(db.String(96))
    adresse = db.Column(db.String(96))
    # Relation un-à-plusieurs : Un lieu peut acceuillir différentes compétitions
    competitions = db.relationship('Competition', back_populates = 'lieu', lazy = 'dynamic')

class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key = True)
    nom = db.Column(db.String(64))
    # Relation un-à-plusieurs : Un club peut avoir plusieurs adhérents
    adherents = db.relationship('Escrimeur', back_populates = 'club', lazy = 'dynamic')

class Categorie(db.Model):
    __tablename__ = 'categorie'
    id = db.Column(db.Integer, primary_key = True)
    libelle = db.Column(db.String(32))
    age_maxi = db.Column(db.Integer)
    # Relation un-à-plusieurs : Une catégorie peut définir plusieurs compétitions
    competitions = db.relationship('Competition', back_populates = 'categorie', lazy = 'dynamic')
    # Relation un-à-plusieurs : Une catégorie peut définir plusieurs classements
    classements = db.relationship('Classement', back_populates = 'categorie', lazy = 'dynamic')

class Arme(db.Model):
    __tablename__ = 'arme'
    id = db.Column(db.Integer, primary_key = True)
    libelle = db.Column(db.String(32))  
    # Relation un-à-plusieurs : Une arme peut définir plusieurs compétitions
    competitions = db.relationship('Competition', back_populates = 'arme', lazy = 'dynamic')
    # Relation un-à-plusieurs : Une arme peut définir plusieurs classements
    classements = db.relationship('Classement', back_populates = 'arme', lazy = 'dynamic')
    

class Escrimeur(db.Model, UserMixin):
    __tablename__ = 'escrimeur'
    num_licence = db.Column(db.String(16), primary_key = True)
    prenom = db.Column(db.String(32))
    nom = db.Column(db.String(32))
    sexe = db.Column(db.String(5))
    date_naissance = db.Column(db.Date)
    # Clé étrangère vers le club
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    # Relation plusieurs-à-un : Un escrimeur est adhérent à un club
    club = db.relationship('Club', back_populates = 'adherents', lazy = 'dynamic')
    # Relation un-à-plusieurs : Un escrimeur peut être dans différents classements
    classements = db.relationship('Classement', back_populates = 'tireur', lazy = 'dynamic')
    # Relation un-à-plusieurs : Un escrimeur peut arbitrer différents matchs
    arbitrages = db.relationship('Match', back_populates = 'arbitre', lazy = 'dynamic')
    # Relation un-à-plusieurs : Un escrimeur peut participer à différents matchs
    participations = db.relationship('Participation', back_populates = 'tireur', lazy = 'dynamic')
    # Relation plusieurs-à-plusieurs : Un escrimeur peut s'inscrire à différentes compétitions
    competitions = db.relationship('Competition', secondary = Inscription, back_populates = 'escrimeurs')
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

class Classement(db.Model):
    __tablename__ = 'classement'
    classement = db.Column(db.Integer)
    points = db.Column(db.Integer)
    # Clé étrangère vers le tireur
    num_licence = db.Column(db.String(16), db.ForeignKey('escrimeur.num_licence'), primary_key = True)
    # Relation plusieurs-à-un : Un classement est lié à un seul tireur
    tireur = db.relationship('Escrimeur', back_populates = 'classements', lazy = 'dynamic')
    # Clé étrangère vers l'arme
    id_arme = db.Column(db.Integer, db.ForeignKey('arme.id'), primary_key = True)
    # Relation plusieurs-à-un : Un classement est définis par une seule arme
    arme = db.relationship('Arme', back_populates = 'classements', lazy = 'dynamic')
    # Clé étrangère vers la catégorie
    id_categorie = db.Column(db.Integer, db.ForeignKey('categorie.id'), primary_key = True)
    # Relation plusieurs-à-un : Un classement est définis par une seule catégorie
    categorie = db.relationship('Categorie', back_populates = 'classements', lazy = 'dynamic')

class Competition(db.Model):
    __tablename__ = 'competition'
    id = db.Column(db.Integer, primary_key = True)
    nom = db.Column(db.String(64))
    date = db.Column(db.Date)
    coefficient = db.Column(db.Integer)
    # Clé étrangère vers le lieu
    id_lieu = db.Column(db.Integer, db.ForeignKey('lieu.id'))
    # Relation plusieurs-à-un : Une compétition se déroule dans un seul lieu
    lieu = db.relationship('Lieu', back_populates = 'competitions', lazy = 'dynamic')
    # Clé étrangère vers l'arme
    id_arme = db.Column(db.Integer, db.ForeignKey('arme.id'), primary_key = True)
    # Relation plusieurs-à-un : Un classement est définis par une seule arme
    arme = db.relationship('Arme', back_populates = 'competitions', lazy = 'dynamic')
    # Clé étrangère vers la catégorie
    id_categorie = db.Column(db.Integer, db.ForeignKey('categorie.id'), primary_key = True)
    # Relation plusieurs-à-un : Un classement est définis par une seule catégorie
    categorie = db.relationship('Categorie', back_populates = 'competitions', lazy = 'dynamic')
    # Relation un-à-plusieurs : Une compétition contient différentes phases
    phases = db.relationship('Phase', back_populates = 'competition', lazy = 'dynamic')
    # Relation plusieurs-à-plusieurs : Une compétition acceuille différents escrimeurs
    escrimeurs = db.relationship('Escrimeur', secondary = Inscription, back_populates = 'competitions')

class Type_phase(db.Model):
    __tablename__ = 'type_phase'
    libelle = db.Column(db.String(32), primary_key = True)
    nb_touches = db.Column(db.Integer)
    # Relation un-à-plusieurs : Un type de phase peut décrire plusieurs phases
    phases = db.relationship('Phase', back_populates = 'type', lazy = 'dynamic')

class Phase(db.Model):
    __tablename__ = 'phase'
    id = db.Column(db.Integer, primary_key = True)
    # Clé étrangère vers la compétition comprenant la phase
    id_competition = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key = True)
    # Relation plusieurs-à-un : Une phase est comprise dans une seule compétition
    competition = db.relationship('Competition', back_populates = 'phases', lazy = 'dynamic')
    # Clé étrangère vers le type de phase
    libelle = db.Column(db.String(32), db.ForeignKey('type_phase.libelle'))
    # Relation plusieurs-à-un : Une phase est décrite par un seul type de phase
    type = db.relationship('Type_phase', back_populates = 'phases', lazy = 'dynamic')
    # Relation un-à-plusieurs : Une compétition contient différentes phases
    matchs = db.relationship('Match', back_populates = 'phase', lazy = 'dynamic')

class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key = True)
    # Clé étrangère vers la phase comprenant le match
    id_phase = db.Column(db.Integer, db.ForeignKey('phase.id'), primary_key = True)
    # Relation plusieurs-à-un : Un match est compris dans une seule phase d'une compétition
    phase = db.relationship('Phase', back_populates = 'matchs', lazy = 'dynamic')
    piste = db.Column(db.Integer)
    etat = db.Column(db.String(16))
    # Clé étrangère vers l'arbitre escrimeur
    num_arbitre = db.Column(db.String(16), db.ForeignKey('escrimeur.num_licence'))
    # Relation plusieurs-à-un : Un match est arbitré par un seul arbitre
    arbitre = db.relationship('Escrimeur', back_populates = 'arbitrages', lazy = 'dynamic')
    # Relation un-à-plusieurs : Un match est arbitré par un seul arbitre
    participations = db.relationship('Participation', back_populates = 'match', lazy = 'dynamic')

class Participation(db.Model):
    __tablename__ = 'participation'
    # Clé étrangère vers le match
    id_match = db.Column(db.Integer, db.ForeignKey('match.id'), primary_key = True)
    # Relation plusieurs-à-un : Une participation est liée à un seul match
    match = db.relationship('Match', back_populates = 'participations', lazy = 'dynamic')
    # Clé étrangère vers le tireur
    id_escrimeur = db.Column(db.String(16), db.ForeignKey('escrimeur.num_licence'), primary_key = True)
    # Relation plusieurs-à-un : Une participation est effectuée par un seul tireur
    tireur = db.relationship('Escrimeur', back_populates = 'participations', lazy = 'dynamic')
    statut = db.Column(db.String(16))
    touches = db.Column(db.Integer)


@login_manager.user_loader
def load_user(num_licence):
    return Escrimeur.query.get(num_licence)
