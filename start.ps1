# Création de l'environnement virtuel
python -m venv venv

# Activation de l'environnement virtuel
. .\venv\Scripts\Activate

# Exécution du script check.py
python check.py

# Vérification du code de retour et installation des dépendances si le code de retour est 0
if ($LastExitCode -eq 0) {
    pip install -r requirements.txt
}

# Chargement de la base de données Flask
flask loadbd

# Exécution de l'application Flask
flask run -h 0.0.0.0 -p 8080

# Désactivation de l'environnement virtuel
deactivate
