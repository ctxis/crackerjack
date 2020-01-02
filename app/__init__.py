import os
import datetime
from flask import Flask, session, render_template
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

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # First we load everything we need in order to end up with a working app.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'crackerjack.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'ThisIsNotTheKeyYouAreLookingFor'
    app.config['SESSION_COOKIE_HTTPONLY'] = True

    # And now we override any custom settings from config.cfg if it exists.
    app.config.from_pyfile('config.py', silent=True)

    # If we have passed any object on app creation (ie testing), override here.
    if config_class is not None:
        app.config.from_object(config_class)

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

    from app.controllers.account import bp as account_bp
    app.register_blueprint(account_bp, url_prefix='/account')

    from app.controllers.install import bp as install_bp
    app.register_blueprint(install_bp, url_prefix='/install')

    from app.controllers.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    csrf.exempt(api_bp)

    from app.lib.base.provider import Provider

    # This is to be able to access settings from any template (shared variables).
    @app.context_processor
    def processor():
        def setting_get(name, default=None):
            provider = Provider()
            return provider.settings().get(name, default)

        def user_setting_get(user_id, name, default=None):
            provider = Provider()
            return provider.user_settings().get(user_id, name, default)

        def template():
            provider = Provider()
            return provider.template()

        return dict(setting_get=setting_get, user_setting_get=user_setting_get, template=template)

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(minutes=20)
        session.modified = True

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    return app


# This has to be at the bottom.
from app.lib.models import user, config, sessions, hashcat, api
