from datetime import datetime
from fruubie import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    # img_url = db.Column(db.String(), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False) # This is a GOOGLE ID
    date = db.Column(db.String(), nullable=False)
    user = db.relationship('User', foreign_keys=[created_by])

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(), nullable=False, unique=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    image = db.Column(db.String())

    
    def __repr__(self):
        return f'<User {self.id}>'
    
    def __str__(self):
        return f'<User {self.id}>'