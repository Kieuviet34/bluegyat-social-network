from flask import Flask
from .config import Config
from .extensions import db, migrate
from app.models import User, Post, PostMedia, Comment, Like, friendships
from .controllers.HomeController import main_bp
from .controllers.AuthController import auth_bp
from .controllers.UserController import user_bp
from .controllers.PostController import post_bp
from .controllers.CommentController import comment_bp
from datetime import datetime, timezone
from .utils.recommender import UserNameTrie

username_trie = UserNameTrie()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    db.init_app(app)
    migrate.init_app(app, db)
    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now(timezone.utc).year
        }
    with app.app_context():
        app.username_trie = username_trie
        for (uname,) in User.query.with_entities(User.username).all():
                app.username_trie.insert(uname)
    #regist bluesprint 
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(post_bp, url_prefix='/posts')
    
    return app