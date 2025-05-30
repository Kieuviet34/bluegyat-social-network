from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.user import User
from flask_login import LoginManager, login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

# Thiết lập Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.record_once
def init_login(state):
    app = state.app
    login_manager.init_app(app)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd   = request.form['password']
        user = User.query.filter_by(username=uname).first()
        if user and user.check_password(pwd):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid credentials.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        email = request.form['email']
        pwd   = request.form['password']
        pwd2 = request.form.get('password2')

        if pwd != pwd2:
            flash('Mật khẩu ko khớp', 'warning')
            return render_template('auth/register.hmtl')
        if User.query.filter_by(username=uname).first():
            flash('Username already taken.', 'warning')
        else:
            u = User(username=uname, full_name=uname, email=email)
            u.set_password(pwd)
            db.session.add(u)
            db.session.commit()

            login_user(u)
            flash('Registration successful! Complete your profile below.', 'success')
            return render_template('auth/register.html',
                                   show_profile_modal = True,
                                   new_user_id=u.user_id)
        
    return render_template('auth/register.html')
