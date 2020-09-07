
from flask import Flask
from datetime import datetime, timedelta, date
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

import os

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME'] = 'bipurna@gmail.com'
app.config['MAIL_PASSWORD'] = 'purnamaya65V'
app.permanent_session_lifetime = timedelta(minutes=15)
db = SQLAlchemy(app)
mail = Mail(app)
from app import routes



