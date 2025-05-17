# tests/test_models_extra.py
import pytest
from app.extensions import db
from app.models import User, Post, PostMedia, Comment, Like


def test_friendship_relation(app):
    # Create two users
    u1 = User(username='user1', full_name='User One', email='u1@example.com', password_hash='h1')
    u2 = User(username='user2', full_name='User Two', email='u2@example.com', password_hash='h2')
    db.session.add_all([u1, u2])
    db.session.commit()

    # Establish friendship (u1 -> u2)
    u1.friends.append(u2)
    db.session.commit()

    # Verify bidirectional relationship
    friends_of_u1 = u1.friends.all()
    befriended_by_u2 = u2.befriended_by 
    assert u2 in friends_of_u1
    assert u1 in befriended_by_u2     



def test_post_comment_like(app):
    # Create a user
    u = User(username='user', full_name='User', email='user@example.com', password_hash='h')
    db.session.add(u)
    db.session.commit()

    # Create a post by the user
    p = Post(user_id=u.user_id, content='Hello world')
    db.session.add(p)
    db.session.commit()

    # Create a comment on the post
    c = Comment(post_id=p.post_id, user_id=u.user_id, content='Nice post!')
    db.session.add(c)
    db.session.commit()
    assert c in p.comments.all()
    assert c.author == u

    # Create a like on the post
    like = Like(user_id=u.user_id, post_id=p.post_id)
    db.session.add(like)
    db.session.commit()
    assert like in p.likes.all()
    assert like in u.likes.all()


def test_post_media_items(app):
    # Create a user and a post
    u = User(username='userx', full_name='User X', email='x@example.com', password_hash='h')
    db.session.add(u)
    db.session.commit()

    p = Post(user_id=u.user_id, content='Post with media')
    db.session.add(p)
    db.session.commit()

    # Add multiple media items
    pm1 = PostMedia(post_id=p.post_id, media_url='http://img1', seq_no=1)
    pm2 = PostMedia(post_id=p.post_id, media_url='http://img2', seq_no=2)
    db.session.add_all([pm1, pm2])
    db.session.commit()

    media_items = p.media_items.order_by(PostMedia.seq_no).all()
    assert len(media_items) == 2
    assert media_items[0].media_url == 'http://img1'
    assert media_items[1].media_url == 'http://img2'
