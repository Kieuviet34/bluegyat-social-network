from datetime import datetime, timezone
from sqlalchemy import Identity
from app.extensions import db

class Post(db.Model):
    __tablename__ = 'POSTS'
    __table_args__ = {'sqlite_autoincrement': True}

    post_id = db.Column(
        'POST_ID', db.Integer,
        db.Identity(start=1, increment=1),
        primary_key=True
    )
    user_id    = db.Column('USER_ID', db.Integer, db.ForeignKey('SC_USERS.USER_ID'), nullable=False)
    content    = db.Column('CONTENT', db.Text, nullable=False)
    media_url  = db.Column('MEDIA_URL', db.String(500))
    created_at = db.Column('CREATED_AT', db.DateTime, default=datetime.now(timezone.utc))

    comments = db.relationship('Comment', backref='post', lazy='dynamic',order_by="Comment.created_at")
    likes    = db.relationship('Like', backref='post', lazy='dynamic')

    def __repr__(self):
        return f"<Post {self.post_id} by {self.user_id}>"