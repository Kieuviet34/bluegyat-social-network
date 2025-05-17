from datetime import datetime, timezone
from app.extensions import db
from sqlalchemy import Identity


class Comment(db.Model):
    __tablename__ = 'COMMENTS'
    __table_args__ = {'sqlite_autoincrement': True}

    comment_id = db.Column(
        'COMMENT_ID', db.Integer,
        db.Identity(start=1, increment=1),
        primary_key=True
    )
    post_id    = db.Column('POST_ID', db.Integer, db.ForeignKey('POSTS.POST_ID'), nullable=False)
    user_id    = db.Column('USER_ID', db.Integer, db.ForeignKey('SC_USERS.USER_ID'), nullable=False)
    content    = db.Column('CONTENT', db.String(1000), nullable=False)
    img_url    = db.Column('IMG_URL', db.String(500))
    created_at = db.Column('CREATED_AT', db.DateTime, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Comment {self.comment_id} on Post {self.post_id}>"