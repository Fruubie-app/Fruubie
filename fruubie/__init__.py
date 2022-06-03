from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from fruubie.config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = 'asdfqwer1234'

db = SQLAlchemy(app)


from fruubie.routes import main
app.register_blueprint(main)

with app.app_context():
    db.create_all()