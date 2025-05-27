from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.comment import Comment
from app.models.post import Post

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@login_required

def add_comment(post_id):
    """
    Handle POST of a new comment on a post.
    Expects form field 'content'.
    """
    # Validate that the post exists
    post = Post.query.get_or_404(post_id)

    # Grab and validate content
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty.', 'warning')
    else:
        comment = Comment(
            post_id=post_id,
            user_id=current_user.user_id,
            content=content
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.', 'success')

    # Redirect back to the post detail
    return redirect(url_for('posts.detail', post_id=post_id))