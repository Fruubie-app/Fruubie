from flask import Flask
from pymongo import MongoClient
from fruubie.config import Config
from os import environ

app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = 'asdfqwer1234'

client = MongoClient('mongodb://localhost:27017/Fruubie')

db = client.get_default_database()

# Collections
users = db.users
posts = db.posts

from fruubie.routes import main
app.register_blueprint(main)

# with app.app_context():
#     db.create_all()