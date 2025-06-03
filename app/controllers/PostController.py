from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.models.user import User
from sqlalchemy import or_
from datetime import datetime

post_bp = Blueprint(
    'posts',
    __name__,
    template_folder='../templates/posts',
    url_prefix='/posts'
)

@post_bp.route('/create', methods=['POST'])
@login_required
def create_post():
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        media = request.form.get('media_url') or None
        
        if not content:
            flash('Post content cannot be empty.', 'warning')
            return redirect(url_for('main.index'))
            
        try:
            # Create and save new post
            post = Post(
                user_id=current_user.user_id,
                content=content,
                media_url=media
            )
            db.session.add(post)
            db.session.commit()
            flash('Post created successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating post: {str(e)}")
            flash('Failed to create post. Please try again.', 'danger')
            
        return redirect(url_for('main.index'))
    return render_template('posts/create.html')

@post_bp.route('/<int:post_id>', methods=['GET'])
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'content': render_template('posts/_post_content.html', post=post),
            'post_id': post.post_id
        })
        
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return render_template('posts/detail.html', post=post, comments=comments)

@post_bp.route('/<int:post_id>/comments', methods=['GET', 'POST'])
@login_required
def post_comments(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        # Parse content from JSON or form data
        content = request.json.get('content', '').strip() if request.is_json else request.form.get('content', '').strip()
            
        # Validate content
        if not content:
            return jsonify({'success': False, 'error': 'Comment cannot be empty'}), 400
        if len(content) > 1000:  # Match DB column size
            return jsonify({'success': False, 'error': 'Comment too long. Maximum 1000 characters.'}), 400
            
        try:
            # Create and save new comment
            comment = Comment(
                post_id=post_id,
                user_id=current_user.user_id,
                content=content
            )
            db.session.add(comment)
            db.session.commit()
            
            # Return consistent author name format
            author_name = comment.author.full_name or comment.author.username
            
            return jsonify({
                'success': True,
                'comment': {
                    'id': comment.comment_id,
                    'content': comment.content,
                    'author': author_name,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'can_modify': True
                }
            })
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating comment: {str(e)}")
            return jsonify({'success': False, 'error': 'Failed to create comment. Please try again.'}), 500
        
    # GET request - return comments
    try:
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
        return jsonify([{
            'id': c.comment_id,
            'content': c.content,
            'author': c.author.full_name or c.author.username,  # Consistent author name format
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M'),
            'can_modify': c.user_id == current_user.user_id
        } for c in comments])
    except Exception as e:
        current_app.logger.error(f"Error fetching comments: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to load comments. Please try again.'}), 500

@post_bp.route('/comments/<int:comment_id>', methods=['POST'])
@login_required
def manage_comment(comment_id):
    # Get comment and verify ownership
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.user_id:
        return jsonify({'success': False, 'error': 'You can only modify your own comments'}), 403

    try:
        # Get action from JSON or form data
        action = request.json.get('action') if request.is_json else request.form.get('action')
        if not action:
            return jsonify({'success': False, 'error': 'No action specified'}), 400
        
        if action == 'delete':
            db.session.delete(comment)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Comment deleted successfully'})
        
        elif action == 'edit':
            # Get and validate content
            content = (request.json.get('content') if request.is_json else request.form.get('content', '')).strip()
            if not content:
                return jsonify({'success': False, 'error': 'Comment cannot be empty'}), 400
            if len(content) > 1000:
                return jsonify({'success': False, 'error': 'Comment too long. Maximum 1000 characters.'}), 400
            
            # Update comment
            comment.content = content
            db.session.commit()
            
            # Return consistent author name format
            author_name = comment.author.full_name or comment.author.username
            
            return jsonify({
                'success': True,
                'message': 'Comment updated successfully',
                'comment': {
                    'id': comment.comment_id,
                    'content': comment.content,
                    'author': author_name,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
                    'can_modify': True
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error managing comment {comment_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process comment action. Please try again.'}), 500

@post_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.user_id, post_id=post_id).first()
    
    if like:
        db.session.delete(like)
        is_liked = False
    else:
        like = Like(user_id=current_user.user_id, post_id=post_id)
        db.session.add(like)
        is_liked = True
    
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'liked': is_liked,
            'count': post.likes.count()
        })
    
    return redirect(request.referrer or url_for('main.index'))

@post_bp.route('/<int:post_id>', methods=['POST'])
@login_required
def manage_post(post_id):
    # Get post and verify ownership
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.user_id:
        return jsonify({'success': False, 'error': 'You can only modify your own posts'}), 403
        
    try:
        # Ensure request is JSON
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
            
        action = request.json.get('action')
        if not action:
            return jsonify({'success': False, 'error': 'No action specified'}), 400
        
        if action == 'delete':
            # Delete associated comments and likes first
            Comment.query.filter_by(post_id=post_id).delete()
            Like.query.filter_by(post_id=post_id).delete()
            db.session.delete(post)
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': 'Post and all associated content deleted successfully'
            })
            
        elif action == 'edit':
            content = request.json.get('content', '').strip()
            if not content:
                return jsonify({'success': False, 'error': 'Post content cannot be empty'}), 400
                
            # Update post
            post.content = content
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Post updated successfully',
                'post': {
                    'id': post.post_id,
                    'content': post.content,
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error managing post {post_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process post action. Please try again.'}), 500

@post_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    # Xóa thủ công các like/comment liên quan trước khi xóa post
    Comment.query.filter_by(post_id=post_id).delete()
    Like.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True})

@post_bp.route('/<int:post_id>/edit', methods=['POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Content cannot be empty'}), 400
    post.content = content
    db.session.commit()
    return jsonify({'success': True, 'content': content})