from datetime import datetime
from app.extensions import db

class Like(db.Model):
    __tablename__ = 'LIKES'

    user_id  = db.Column('USER_ID', db.Integer, db.ForeignKey('SC_USERS.USER_ID'), primary_key=True)
    post_id  = db.Column('POST_ID', db.Integer, db.ForeignKey('POSTS.POST_ID'), primary_key=True)
    liked_at = db.Column('LIKED_AT', db.DateTime, default=datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<Like {self.user_id}->{self.post_id}>"