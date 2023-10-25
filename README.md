# Projet 2 : Gestion – Compétition Escrime
---
Titouan COULON, Noam DOUCET, Anthony GARDELLE, Arthur GOUDAL, Killian OUZET
---
---
# Reformulation de la commande
Avec l'objectif final de gérer plusieurs compétitions d'escrime nous devions créer une application où l'on peut :
+ Répondre à la définition de la compétition.
+ Inscrire à la compétition un nombre de « tireurs » ou « tireuses » non limité.
+ Inscrire des arbitres au compétition.
+ Répartire automatique les compétiteurs en poule de 5 à 9 participants, selon
  les règles de la fédération.
+ Répartire des poules ou les matches d’élimination sur les pistes disponibles.
+ Gérer des phases d’élimination directe après les phases de poule.
+ Éditer sur application des feuilles de match (feuille de score données aux arbitres).
+ Établir un classement provisoire (après les poules) et d’un classement final après les matchs d’élimination.
+ Afficher sur grand écran des classements et de l’arbre du tableau d’élimination et des résultats.

Spécifications techniques :
+ On considère qu’il existe une base de données régionale des escrimeurs qui
  pratiquent la compétition. Si un joueur s’inscrit pour la première fois à une
  compétition, l’application l’ajoutera à cette base.
+ L’application archivera les compétitions gérées par le club et mettra à jour les
  classements des compétiteurs. Attention, le classement à l’issue de la compétition
  n’est qu’un élément du classement à proprement parler d’un joueur. (Fusion avec
  des BD externe)
+ On considère qu'il existe 6 armes (fleuret homme, fleuret femme, épée homme, épée femme, sabre homme
et sabre femme) et 9 catégories (U13, U15, U17, U20, senior, V1, V2, V3, V4).
---
# Mise en place de l'application
Création de l'environnement virtuelle
---
```
python3 -m venv <nom_environnement> (Windows)
virtualenv -p python3 <nom_environnement> (Linux)
```
Activation de l'environnement virtuel
---
```
<nom_environnement>\Scripts\Activate.ps1 (Windows)
source <nom_environnement>/bin/activate (Linux)
```
Installation des packages nécessaire
---
```
    pip install flask
    pip install python-dotenv
    pip install pyYAML
    pip install bootstrap-flask
    pip install flask-sqlalchemy
    pip install flask-wtf
    pip install flask-login
    pip install --force-reinstall Werkzeug==2.3.0
```