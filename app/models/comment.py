from datetime import datetime
from app.extensions import db

class Comment(db.Model):
    __tablename__ = 'COMMENTS'

    comment_id = db.Column('COMMENT_ID', db.Integer, primary_key=True)
    post_id    = db.Column('POST_ID', db.Integer, db.ForeignKey('POSTS.POST_ID'), nullable=False)
    user_id    = db.Column('USER_ID', db.Integer, db.ForeignKey('SC_USERS.USER_ID'), nullable=False)
    content    = db.Column('CONTENT', db.String(1000), nullable=False)
    img_url    = db.Column('IMG_URL', db.String(500))
    created_at = db.Column('CREATED_AT', db.DateTime, default=datetime.now(datetime.timezone.utc))

    def __repr__(self):
        return f"<Comment {self.comment_id} on Post {self.post_id}>"