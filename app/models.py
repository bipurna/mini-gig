from datetime import datetime,time
from app import db
import os



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    user_profile = db.Column(db.String(20),nullable=False,default="default.jpg")
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    dob = db.Column(db.DateTime(), nullable=False)
    nationality = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    acitve = db.Column(db.Boolean(), nullable=False, default=False)
    hashCode = db.Column(db.String(120))
    created_at = db.Column(db.DateTime(), nullable=False,
                           default=datetime.now)
    posts = db.relationship('Posts', backref="user",
                            lazy='dynamic')

    def __init__(self, username, name, email, password, dob, nationality, gender):
        self.username = username
        self.name = name
        self.email = email
        self.password = password
        self.dob = dob
        self.nationality = nationality
        self.gender = gender

    def __repr__(self):
        return f"User('{self.username},{self.name}')"


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    posted_on = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    replies = db.relationship('Replies', backref="posts")

    def __init__(self, post, user_id):
        self.post = post
        self.user_id = user_id

    def __repr__(self):
        return f"Posts('{self.user_id}')"


class Replies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply = db.Column(db.Text, nullable=False)
    replied_on = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id"))
    post_id = db.Column(db.Integer, db.ForeignKey(
        "posts.id"))

    def __init__(self, reply, user_id, post_id):
        self.reply = reply
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        return f"Replies('{self.user_id}')"
