
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db
from datetime import datetime, timezone

friendships = db.Table(
    'FRIENDSHIPS',
    db.Column('USER_ID', db.Integer, db.ForeignKey('SC_USERS.USER_ID'), primary_key=True),
    db.Column('FRIEND_ID', db.Integer, db.ForeignKey('SC_USERS.USER_ID'), primary_key=True),
    db.Column('STATUS', db.String(20), default='PENDING'),
    db.Column('REQUESTED_AT', db.DateTime, default=datetime.now(timezone.utc)),
    db.Column('ACCEPTED_AT', db.DateTime, nullable=True)
)
class User(db.Model):
    __tablename__ = 'SC_USERS'

    user_id         = db.Column('USER_ID', db.Integer, primary_key=True)
    username        = db.Column('USERNAME', db.String(50), unique=True, nullable=False)
    full_name       = db.Column('FULL_NAME', db.String(100))
    email           = db.Column('EMAIL', db.String(100), unique=True, nullable=False)
    password_hash   = db.Column('PASSWORD_HASH', db.String(256), nullable=False)
    profile_img_url = db.Column('PROFILE_IMG_URL', db.String(500))
    cover_img_url   = db.Column('COVER_IMG_URL', db.String(500))
    created_at      = db.Column('CREATED_AT', db.DateTime, default=datetime.now(timezone.utc))

    posts    = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes    = db.relationship('Like', backref='user', lazy='dynamic')
    friends  = db.relationship(
        'User', secondary=friendships,
        primaryjoin=user_id==friendships.c.USER_ID,
        secondaryjoin=user_id==friendships.c.FRIEND_ID,
        backref='befriended_by', lazy='dynamic'
    )

    def __repr__(self):
        return f"<User {self.username}>"

