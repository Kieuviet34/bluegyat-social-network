from flask import Blueprint, render_template
from app.models.post import Post

main_bp = Blueprint(
    'main',
    __name__,
    template_folder='../templates'
)

@main_bp.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    return render_template('index.html', post = posts)