# app/models/notification.py

from datetime import datetime, timezone
from sqlalchemy import Identity
from app.extensions import db

class Notification(db.Model):
    __tablename__ = 'NOTIFICATIONS'

    notif_id = db.Column(
        'NOTIF_ID', 
        db.Integer, 
        db.Identity(start=1, increment=1), 
        primary_key=True
    )
    recipient_user_id = db.Column(
        'RECIPIENT_USER_ID', 
        db.Integer, 
        db.ForeignKey('SC_USERS.USER_ID'), 
        nullable=False
    )
    actor_user_id = db.Column(
        'ACTOR_USER_ID', 
        db.Integer, 
        db.ForeignKey('SC_USERS.USER_ID'), 
        nullable=True
    )
    type = db.Column('TYPE', db.String(30), nullable=False)
    entity_id = db.Column('ENTITY_ID', db.Integer)
    entity_type = db.Column('ENTITY_TYPE', db.String(20))
    message = db.Column('MESSAGE', db.String(4000))
    is_read = db.Column('IS_READ', db.String(1), default='N', nullable=False)
    created_at = db.Column(
        'CREATED_AT', 
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    recipient = db.relationship(
        'User', 
        foreign_keys=[recipient_user_id], 
        backref=db.backref('notifications_received', lazy='dynamic')
    )
    actor = db.relationship(
        'User', 
        foreign_keys=[actor_user_id], 
        backref=db.backref('notifications_sent', lazy='dynamic')
    )

    def __repr__(self):
        return f"<Notification {self.notif_id} to User {self.recipient_user_id}>"
