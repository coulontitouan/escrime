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
Pour lancer l'application il vous suffit d'éxécuter les commande bash suivante :
```
git clone https://github.com/coulontitouan/escrime.git
cd escrime
source start.sh (Linux)
.\start.ps1 (Windows)
```
Ensuite il vous suffit de cliquer sur "http://192.168.28.66:8080"
```
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://192.168.28.66:8080
Press CTRL+C to quit
```
Pour fermer l'application il suffit de faire la combinaison de touche CTRL+C dans le terminal
---
# Rapports Individuels Finaux

## Killian OUZET
<div align="justify">

Durant cette dernière semaine de projet sur notre application de gestion de compétition d'escrime j’ai pu principalement faire des correctifs ainsi qu’ ajouter des fonctionnalités mineures ayant pour objectif d’améliorer l’utilisation de l’application par les utilisateurs. 

Les premiers jours de cette semaine je me suis donc concentré en priorité sur la correction de différentes fonctionnalités qui avaient été déréglées du à certains changements backend. En effet, lors d’un projet il arrive que des anciennes fonctions changent à cause de l’avancé du projet mais que nous oublions donc de modifier des fonctionnalités en lien. Et cette situation est arrivée, le classement intra-poule n’était plus correctement affiché. Noam qui avait développé cela précédemment m’a donc expliqué son code et j’ai pu ainsi le modifier pour qu’il soit en accord avec les derniers changements de l’application afin de ré-afficher dans le bon ordre les escrimeurs des poules. À la suite de cela j’ai corrigé la répartition des poules, qui se fait lorsqu’un admin clique sur un bouton afin de lancer la compétition. Après avoir fini ces corrections je me suis tourné vers l’ajout de vérification pour les fonctionnalités de l’appli, comme par exemple la vérification du statut de l’utilisateur pour l’accès aux pages ou bien enlever les boutons Inscription désinscription si la compétition a commencé. Et enfin, j’ai terminé cette semaine par rendre fonctionnel l’historique des compétitions d’un escrimeur dans sa page profil. Fonctionnalités que j’avais préparées lors d’une semaine précédente mais que je n’avais pas faites car ce n’était pas très important à ce moment. Je peux aussi citer la petite animation en javascript que j’ai travaillé pendant des moments creux de la semaine qui consiste à l’allongement de l’épée de l’escrimeur du logo en haut à gauche de la page lorsque l’on clique dessus.

En revanche, ce vendredi je n’ai pas pu participer à l'avancée du projet car je n’étais pas présent ( entretien avec une entreprise) et donc la soutenance aussi.

### Bilan personnel
Pour conclure ce bilan, je dirai que j’ai apprécié participé à ce projet et le sujet était intéressant en plus de permettre un vrai travail derrière. Mais ce qui m’a principalement marqué durant cette SAE est le temps donné. En effet c’était la première fois que nous avions plusieurs semaines complètes pour un projet et je trouve cela beaucoup plus plaisant. ça nous permet déjà de rendre quelque chose de beaucoup plus travaillé et réfléchi avec une continuité durant l’année. Nous pouvons aussi utiliser d’autres technologies que nous avons découvertes tout du long du semestre. Je dirai donc que je préfère même avec un projet qui dure plutôt qu’un que nous fassions une fois puis que nous oublions.
</div>

---
## Anthony Gardelle
<div align="justify">

Lors des premiers jours de cette dernière semaine de SAE, je me suis principalement occupé du tableau avec le récapitulatif des touches lors de phases de poules en collaboration avec Titouan. Cet affichage m’a pris un peu plus de temps que prévu à réaliser, j’avais un affichage des bordures qui ne se faisait pas en raison du javascript utilisé pour la création des cases noires dans le tableau.Titouan m’a donc aidé et expliquait comment le résoudre.  Le tableau est un modèle identique à celui espéré avec un ajout des touches données par le joueur. Pour réaliser ce tableau j’ai utilisé les balises html classique à la réalisation d’un tableau (table, tbody, td, tr, ...) et aussi un peu de javascript. 

Enfin pour la deuxième partie de la semaine je me suis occupé de la page d’information sur un escrimeur participant à une compétition individuelle. La réalisation de cette page a été assez simple et ne m’a pas trop pris de temps car nous avons une simplicité d’accès aux données grâce à une bonne conception de la BD principalement réalisée par Arthur. Dans cette page on peut retrouver des informations globales sur l’escrimeur ainsi qu’un récapitulatif des matchs effectué par l’escrimeur (adversaire, phase, résultat, …). J’ai donc pour accéder à cette page ajouter un indicateur en passant sa souris sur la ligne du tableau réserver à l’escrimeur sur lequel nous avons envie de nous renseigner dans le classement provisoire de la compétition.

Cette dernière semaine de projet a été pour moi une semaine éprouvante avec une grande diversité de langage utilisé, après plusieurs semaines de pause avec les semaines précédentes, j’ai pu avoir un œil différent sur le projet ce qui a permis l’amélioration de mon esprit critique. En travaillant avec mes camarades, j’ai pu améliorer mes compétences en programmation, tout cela a été possible grâce à une excellente cohésion avec le groupe et une organisation du travail millimétrée.
</div>
