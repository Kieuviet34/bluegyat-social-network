from flask import Blueprint, render_template, abort, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.post import Post

user_bp = Blueprint(
    'user',
    __name__,
    template_folder='../templates/users',
    url_prefix='/users'
)

@user_bp.route('/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)

    # Only allow editing your own profile
    if request.method == 'POST':
        if user_id != current_user.user_id:
            abort(403)
        # Grab form fields
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip()
        profile   = request.form.get('profile_img_url', '').strip() or None
        cover     = request.form.get('cover_img_url', '').strip()   or None

        # Basic validation
        if not full_name or not email:
            flash('Name and email cannot be empty.', 'warning')
        else:
            user.full_name       = full_name
            user.email           = email
            user.profile_img_url = profile
            user.cover_img_url   = cover
            db.session.commit()
            flash('Profile updated.', 'success')
            return redirect(url_for('user.profile', user_id=user_id))

    # ORDER BY on actual column
    posts = (Post.query
                 .filter_by(user_id=user_id)
                 .order_by(Post.created_at.desc())
                 .all())

    return render_template('profile.html', user=user, posts=posts)