from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.post import Post
from app.models.comment import Comment

post_bp = Blueprint(
    'posts',
    __name__,
    template_folder='../templates/posts',
    url_prefix='/posts'
)

@post_bp.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('posts/index.html', posts=posts)

@post_bp.route('/create', methods=['GET', 'POST'])
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
@post_bp.route('/<int:post_id>')
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query \
        .filter_by(post_id=post_id) \
        .order_by(Comment.created_at.asc()) \
        .all()
    return render_template('posts/detail.html', post=post, comments=comments)
