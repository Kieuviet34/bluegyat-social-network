from sqlalchemy import Identity
from app.extensions import db

class PostMedia(db.Model):
    __tablename__ = 'POST_MEDIA'
    __table_args__ = {'sqlite_autoincrement': True}

    media_id = db.Column(
        'MEDIA_ID', db.Integer,
        db.Identity(start=1, increment=1),
        primary_key=True
    )
    post_id   = db.Column('POST_ID', db.Integer, db.ForeignKey('POSTS.POST_ID'), nullable=False)
    media_url = db.Column('MEDIA_URL', db.String(500), nullable=False)
    seq_no    = db.Column('SEQ_NO', db.Integer, default=1)

    post = db.relationship('Post', backref=db.backref('media_items', lazy='dynamic'))

    def __repr__(self):
        return f"<PostMedia {self.media_id} for Post {self.post_id}>"