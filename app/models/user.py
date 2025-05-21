from datetime import datetime, timezone
from werkzeug.security     import generate_password_hash, check_password_hash
from flask_login           import UserMixin
from sqlalchemy            import Identity
from app.extensions        import db

friendships = db.Table(
    'FRIENDSHIPS',
    db.Column('USER_ID',    db.Integer, db.ForeignKey('SC_USERS.USER_ID'), primary_key=True),
    db.Column('FRIEND_ID',  db.Integer, db.ForeignKey('SC_USERS.USER_ID'), primary_key=True),
    db.Column('STATUS',     db.String(20), default='PENDING'),
    db.Column('REQUESTED_AT',db.DateTime, default=datetime.now(timezone.utc)),
    db.Column('ACCEPTED_AT', db.DateTime, nullable=True)
)

class User(UserMixin, db.Model):
    __tablename__  = 'SC_USERS'
    __table_args__ = {'sqlite_autoincrement': True}

    user_id = db.Column(
        'USER_ID', db.Integer, 
        Identity(start=1, increment=1),  # Oracle identity
        primary_key=True
    )
    username        = db.Column('USERNAME',         db.String(50),  unique=True, nullable=False)
    full_name       = db.Column('FULL_NAME',        db.String(100))
    email           = db.Column('EMAIL',            db.String(100), unique=True, nullable=False)
    password_hash   = db.Column('PASSWORD_HASH',    db.String(256), nullable=False)
    profile_img_url = db.Column('PROFILE_IMG_URL',  db.String(500))
    cover_img_url   = db.Column('COVER_IMG_URL',    db.String(500))
    created_at      = db.Column('CREATED_AT',       db.DateTime, default=datetime.now(timezone.utc))

    # Quan hệ
    posts    = db.relationship('Post',    backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    likes    = db.relationship('Like',    backref='user',   lazy='dynamic')
    friends  = db.relationship(
        'User', secondary=friendships,
        primaryjoin   = user_id == friendships.c.USER_ID,
        secondaryjoin = user_id == friendships.c.FRIEND_ID,
        backref       = db.backref('befriended_by', lazy='dynamic'),
        lazy          = 'dynamic'
    )

    def set_password(self, password: str):
        """Hash và lưu vào password_hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """So sánh password nhập vào với hash đã lưu."""
        return check_password_hash(self.password_hash, password)
    def get_id(self):
        return str(self.user_id)
    def __repr__(self):
        return f"<User {self.username}>"
