from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User
from sqlalchemy import or_


post_bp = Blueprint(
    'posts',
    __name__,
    template_folder='../templates/posts',
    url_prefix='/posts'
)

@post_bp.route('/')
def index():
    q = request.args.get('q')
    # If the param is present but empty, ask the user to type something
    if 'q' in request.args and not q.strip():
        flash("Please enter a username to search.", "warning")
        return redirect(url_for('posts.index'))

    # Base query joins User so we can filter by name
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

    # If they searched and got zero, suggest
    suggestions = []
    if q and not posts:
        suggestions = current_app.username_trie.suggest(q)

    return render_template(
        'posts/index.html',
        posts=posts,
        suggestions=suggestions,
        q=q or ""
    )

@post_bp.route('/create', methods=['POST'])
@login_required
def create_post():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        media   = request.form.get('media_url') or None
        if not content:
            flash('Content must not be empty.', 'warning')
            return redirect(url_for('posts.create_post'))
        p = Post(user_id=current_user.user_id, content=content, media_url=media)
        db.session.add(p)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('posts.index'))
    return render_template('posts/create.html')
@post_bp.route('/<int:post_id>', methods=['GET', 'POST'])
def detail(post_id):
    # Fetch the post or 404
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        # Handle comment submission
        content = request.form.get('content', '').strip()
        if not content:
            flash('Comment cannot be empty.', 'warning')
        else:
            c = Comment(
                post_id=post_id,
                user_id=current_user.user_id,
                content=content
            )
            db.session.add(c)
            db.session.commit()
            flash('Comment added.', 'success')
        # Redirect to GET to avoid double‐submit
        return redirect(url_for('posts.detail', post_id=post_id))

    # GET: load comments for display
    comments = (Comment.query
                .filter_by(post_id=post_id)
                .order_by(Comment.created_at.asc())
                .all())
    return render_template('posts/detail.html', post=post, comments=comments)