from flask import Blueprint, render_template, abort
from app.extensions import db
from app.models.user import User
from flask_login import login_required, current_user

user_bp = Blueprint(
    'user',
    __name__,
    template_folder='../templates/users',
    url_prefix='/users'
)

@user_bp.route('/<int:user_id>')
@login_required
def profile(user_id):
    """
    Trang profile của user.
    Nếu user_id khác current_user.user_id, bạn có thể
    chỉ hiển thị công khai (public fields).
    """
    user = User.query.get(user_id)
    if not user:
        abort(404)
    posts = user.posts.order_by(db.desc('created_at')).all()
    return render_template('profile.html', user=user, posts=posts)