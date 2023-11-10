from .app import db, login_manager
from sqlalchemy import *
from flask_login import UserMixin

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
        naissance = self.date_naissance.strftime('%d/%m/%Y')
        return ([self.nom, self.prenom, naissance, self.num_licence, self.nationalite],
                [self.num_licence, self.mot_de_passe])

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
        return self.tireur.to_csv()[0] + self.tireur.club.to_csv() + [self.points, self.rang]

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

    def get_tireurs_phase(self, id_phase):
        joueurs = set()
        matchs = Match.query.filter_by(id_phase = (self.id,id_phase))
        for m in matchs:
            participations = Participation.query.filter_by(id_match = m.id)
            for p in participations:
                joueurs.add(Escrimeur.query.get(p.id_escrimeur))
        return joueurs
    
    def get_arbitre_phase(self, id_phase):
        return Escrimeur.query.get(Match.query.filter_by(id_phase = (self.id,id_phase)).first().num_arbitre)
    
    def get_points(self, id_tireur):
        return Resultat.query.get((self.id,id_tireur)).points
    
    def get_categorie(self):
        return self.categorie
    
    def get_arme(self):
        return self.arme
    
    def get_lieu(self):
        return self.lieu

    def get_tireurs_phase(self, id_phase):
        joueurs = set()
        matchs = Match.query.filter_by(id_phase = (self.id,id_phase))
        for m in matchs:
            participations = Participation.query.filter_by(id_match = m.id)
            for p in participations:
                joueurs.add(Escrimeur.query.get(p.id_escrimeur))
        return joueurs
    
    def get_arbitre_phase(self, id_phase):
        return Escrimeur.query.get(Match.query.filter_by(id_phase = (self.id,id_phase)).first().num_arbitre)
    
    def get_points(self, id_tireur):
        return Resultat.query.get((self.id,id_tireur)).points
    
    def get_categorie(self):
        return self.categorie
    
    def get_arme(self):
        return self.arme
    
    def get_lieu(self):
        return self.lieu

    def get_tireurs_phase(self, id_phase):
        joueurs = set()
        matchs = Match.query.filter_by(id_phase = (self.id,id_phase))
        for m in matchs:
            participations = Participation.query.filter_by(id_match = m.id)
            for p in participations:
                joueurs.add(Escrimeur.query.get(p.id_escrimeur))
        return joueurs
    
    def get_arbitre_phase(self, id_phase):
        return Escrimeur.query.get(Match.query.filter_by(id_phase = (self.id,id_phase)).first().num_arbitre)
    
    def get_points(self, id_tireur):
        return Resultat.query.get((self.id,id_tireur)).points
    
    def get_categorie(self):
        return self.categorie
    
    def get_arme(self):
        return self.arme
    
    def get_lieu(self):
        return self.lieu
    
    def to_titre_csv(self):
        res = ''
        split = self.nom.split(' ')
        for mot in split:
            res += mot[0].upper() + mot[1:]
        res += '_'
        date_csv = self.date.strftime('%d/%m/%Y')
        for carac in date_csv:
            if carac == '/':
                res += '-'
            else:
                res += carac
        return res + '_' + str(self.id)

    def to_csv(self):
        date_csv = self.date.strftime('%d/%m/%Y')
        return [self.nom, date_csv, self.sexe] + self.categorie.to_csv() + self.arme.to_csv() + [self.coefficient] + self.lieu.to_csv()

class Type_phase(db.Model):
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
    type = db.relationship('Type_phase', back_populates = 'phases')
    # Relation un-à-plusieurs : Une compétition contient différentes phases
    matchs = db.relationship('Match', back_populates = 'phase')
    __table_args__ = (
        PrimaryKeyConstraint(id, id_competition),
        {},
    )


    def to_csv(self):
        return [self.id, self.libelle]

class Match(db.Model):
    __tablename__ = 'match'
    id = db.Column(db.Integer(), primary_key = True)
    # Clé étrangère vers la compétition comprenant le match
    id_competition = db.Column(db.Integer(), db.ForeignKey('competition.id'), primary_key = True)
    # Relation plusieurs-à-un unidirectionnel : Un match est compris dans une seule compétition
    competition = db.relationship('Competition')
    # Clé étrangère vers la phase comprenant le match
    id_phase = db.Column(db.Integer(), db.ForeignKey('phase.id'), primary_key = True)
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


    def to_csv(self):
        return [self.id, self.participations[0], self.participations[1], self.num_arbitre, self.piste, self.etat] + self.phase.to_csv()

class Participation(db.Model):
    __tablename__ = 'participation'
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
        PrimaryKeyConstraint(id_match, id_escrimeur),
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




def get_lieu(nom, adresse, ville):
    """Fonction qui permet de récupérer un lieu dans la base de données"""
    return Lieu.query.filter_by(nom = nom, adresse = adresse, ville = ville).first()
def get_lieu(nom, adresse, ville):
    """Fonction qui permet de récupérer un lieu dans la base de données"""
    return Lieu.query.filter_by(nom = nom, adresse = adresse, ville = ville).first()

def get_arme(id):
    """Fonction qui permet de récupérer une arme dans la base de données"""
    return Arme.query.get(id)

def get_all_armes():
    """Fonction qui permet de récupérer toutes les armes dans la base de données"""
    return Arme.query.all()

def cree_liste(liste) :
    cpt = 1
    liste2 = []
    for x in liste :
        liste2.append((cpt, x.libelle))
        cpt += 1
    return liste2

def get_categorie(id):
    """Fonction qui permet de récupérer une catégorie dans la base de données"""
    return Categorie.query.get(id)

def get_all_categories():
    """Fonction qui permet de récupérer toutes les catégories dans la base de données"""
    return Categorie.query.all()

def get_max_competition_id():
    """Fonction qui permet de récupérer l'id de la dernière compétition créée"""
    """Fonction qui permet de récupérer l'id de la dernière compétition créée"""
    if Competition.query.count() == 0:
        return 0
    return Competition.query.order_by(desc(Competition.id)).first().id

@login_manager.user_loader
def load_user(num_licence):
    return Escrimeur.query.get(num_licence)

def get_compet_accueil():
    return Competition.query.all()

def get_club(id):
    return Club.query.get(id)

def get_typephase(id):
    return Type_phase.query.get(id)

def get_match(id):
    return Match.query.get(id)

def get_competition(id):
    return Competition.query.get(id)

def get_participation(id):
    return Participation.query.get(id)

def get_all_competitions():
    return Competition.query.all()

# def get_nb_tireurs_poule(id_poule):
#     poule = get_phase(id_poule)
@login_manager.user_loader
def load_user(num_licence):
    return Escrimeur.query.get(num_licence)

def get_compet_accueil():
    return Competition.query.all()

def get_club(id):
    return Club.query.get(id)

def get_typephase(id):
    return Type_phase.query.get(id)

def get_match(id):
    return Match.query.get(id)

def get_competition(id):
    return Competition.query.get(id)

def get_participation(id):
    return Participation.query.get(id)

def get_all_competitions():
    return Competition.query.all()

# def get_nb_tireurs_poule(id_poule):
#     poule = get_phase(id_poule)