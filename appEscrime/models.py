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

class Escrimeur(db.Model):
    __tablename__ = 'escrimeur'
    num_licence = db.Column(db.Integer, primary_key = True)
    prenom = db.Column(db.String(32))
    nom = db.Column(db.String(32))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    club = db.relationship('Club', backref = db.backref('escrimeur', lazy = 'dynamic'))