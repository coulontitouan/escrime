#!/bin/bash
virtualenv -p python3 $1
source $1/bin/activate
pip install flask
pip install python-dotenv
pip install pyYAML
pip install bootstrap-flask
pip install flask-sqlalchemy
pip install flask-wtf
pip install flask-login
pip install --force-reinstall Werkzeug==2.3.0
cd appEscrime
flask run -h 0.0.0.0 -p 8080
```