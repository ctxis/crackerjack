import os, datetime
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
csrf = CSRFProtect()


def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'crackerjack.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'ThisIsNotTheKeyYouAreLookingFor'

    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)

    from app.controllers.home import bp as home_bp
    app.register_blueprint(home_bp, url_prefix='/')

    from app.controllers.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.controllers.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.controllers.sessions import bp as sessions_bp
    app.register_blueprint(sessions_bp, url_prefix='/sessions')

    # @app.before_request
    # def before_request():
    #     session.permanent = True
    #     app.permanent_session_lifetime = datetime.timedelta(minutes=1)
    #     session.modified = True

    return app


# This has to be at the bottom.
from app.lib.models import user, config, session
