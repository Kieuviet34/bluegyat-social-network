from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required
from sqlalchemy import or_
from app.extensions import db
from app.models.post import Post
from app.models.user import User


main_bp = Blueprint(
    'main',
    __name__,
    template_folder='../templates'
)

@main_bp.route('/')
@login_required
def index():
    # exactly same search logic as in posts.index
    q = request.args.get('q')
    if 'q' in request.args and not q.strip():
        flash("Please enter a username to search.", "warning")
        return render_template('index.html', posts=[], suggestions=[], q="")

    query = Post.query.join(User, Post.user_id == User.user_id)
    if q:
        ilike_q = f"%{q}%"
        query = query.filter(
            or_(
                User.username.ilike(ilike_q),
                User.full_name.ilike(ilike_q)
            )
        )
    posts = query.order_by(Post.created_at.desc()).all()

    suggestions = []
    if q and not posts:
        suggestions = current_app.username_trie.suggest(q)

    return render_template(
        'index.html',
        posts=posts,
        suggestions=suggestions,
        q=q or ""
    )

@main_bp.route('/search/users')
def search_users():
    q = request.args.get('q', '').strip().lower()
    if not q:
        return []
    users = User.query.filter(User.username.ilike(f"%{q}%")).limit(10).all()
    return [{
        'username': u.username,
        'avatar_url': u.profile_img_url or '/static/img/default-avatar.png'
    } for u in users]