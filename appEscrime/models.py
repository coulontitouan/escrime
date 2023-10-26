from .app import db
from sqlalchemy import *
from flask_login import UserMixin


class Lieu(db.Model):
    __tablename__ = 'lieu'
    id = db.Column(db.Integer, primary_key = True)
    nom = db.Column(db.String(96))
    adresse = db.Column(db.String(96))

class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key = True)
    nom = db.Column(db.String(64))

class Categorie(db.Model):
    __tablename__ = 'categorie'
    id = db.Column(db.Integer, primary_key = True)
    libelle = db.Column(db.String(32))
    age_maxi = db.Column(db.Integer)

class Escrimeur(db.Model, UserMixin):
    __tablename__ = 'escrimeur'
    num_licence = db.Column(db.Integer, primary_key = True)
    prenom = db.Column(db.String(32))
    nom = db.Column(db.String(32))
    sexe = db.Column(db.String(5))
    date_naissance = db.Column(db.Date)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    club = db.relationship('Club', backref = db.backref('escrimeur', lazy = 'dynamic'))
    mot_de_passe = db.Column(db.String(64), default = '')

    def set_mdp(self, mdp):
        self.mot_de_passe = mdp

class Arme(db.Model):
    __tablename__ = 'arme'
    id = db.Column(db.Integer, primary_key = True)
    libelle = db.Column(db.String(32))  

class Categorisation(db.Model):
    __tablename__ = 'categorisation'
    classement = db.Column(db.Integer)
    points = db.Column(db.Integer)
    num_licence = db.Column(db.Integer, db.ForeignKey('escrimeur.num_licence'), primary_key = True)
    tireur = db.relationship('Escrimeur', backref = db.backref('categorisation', lazy = 'dynamic'))
    id_arme = db.Column(db.Integer, db.ForeignKey('arme.id'), primary_key = True)
    arme = db.relationship('Arme', backref = db.backref('categorisation', lazy = 'dynamic'))
    id_categorie = db.Column(db.Integer, db.ForeignKey('categorie.id'), primary_key = True)
    categorie = db.relationship('Categorie', backref = db.backref('categorisation', lazy = 'dynamic'))

class Competition(db.Model):
    __tablename__ = 'competition'
    id = db.Column(db.Integer, primary_key = True)
    nom = db.Column(db.String(64))
    date = db.Column(db.Date)
    coefficient = db.Column(db.Integer)
    id_lieu = db.Column(db.Integer, db.ForeignKey('lieu.id'))
    lieu = db.relationship('Lieu', backref = db.backref('competition', lazy = 'dynamic'))

class Inscription(db.Model):
    __tablename__ = 'inscription'
    id_competition = db.Column(db.Integer, db.ForeignKey('competition'), primary_key = True)
    competition = db.relationship('Competition', backref = db.backref('inscription', lazy = 'dynamic'))
    id_escrimeur = db.Column(db.Integer, db.ForeignKey('escrimeur'), primary_key = True)
    escrimeur = db.relationship('Escrimeur', backref = db.backref('inscription', lazy = 'dynamic'))

class Type_phase(db.Model):
    __tablename__ = 'type_phase'
    libelle = db.Column(db.String(32), primary_key = True)
    nb_touches = db.Column(db.Integer)

class Phase(db.Model):
    __tablename__ = 'phase'
    id = db.Column(db.Integer, primary_key = True)
    id_competition = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key = True)
    competition = db.relationship('Competition', backref = db.backref('phase', lazy = 'dynamic'))
    libelle = db.Column(db.String(32), db.ForeignKey('type_phase.id'))
    type_phase = db.relationship('Type_phase', backref = db.backref('phase', lazy = 'dynamic'))

class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer, primary_key = True)
    id_phase = db.Column(db.Integer, db.ForeignKey('phase.id'), primary_key = True)
    phase = db.relationship('Phase', backref = db.backref('match', lazy = 'dynamic'))
    id_competition = db.Column(db.Integer, db.ForeignKey('competition.id'), primary_key = True)
    competition = db.relationship('Competition', backref = db.backref('match', lazy = 'dynamic'))
    piste = db.Column(db.Integer)
    etat = db.Column(db.String(16))
    num_arbitre = db.Column(db.Integer, db.ForeignKey('escrimeur.num_licence'))
    arbitre = db.relationship('Escrimeur', backref = db.backref('match', lazy = 'dynamic'))

class Participation(db.Model):
    __tablename__ = 'participation'
    id_match = db.Column(db.Integer, db.ForeignKey('match'), primary_key = True)
    match = db.relationship('Match', backref = db.backref('participation', lazy = 'dynamic'))
    id_escrimeur = db.Column(db.Integer, db.ForeignKey('escrimeur'), primary_key = True)
    escrimeur = db.relationship('Escrimeur', backref = db.backref('participation', lazy = 'dynamic'))
    statut = db.Column(db.String(16))
    touches = db.Column(db.Integer)
