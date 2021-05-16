import os
import datetime
from flask import Flask, session, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_crontab import Crontab
from app import version


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
csrf = CSRFProtect()
crontab = Crontab()


def create_app(config_class=None):
    # Make sure the instance path is within the ./data folder.
    data_instance_path = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'data', 'instance'))

    app = Flask(__name__, instance_path=data_instance_path, instance_relative_config=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # First we load everything we need in order to end up with a working app.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'crackerjack.sqlite3')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'ThisIsNotTheKeyYouAreLookingFor'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    # The referrer is disabled further down in the response headers.
    app.config['WTF_CSRF_SSL_STRICT'] = False

    # And now we override any custom settings from config.cfg if it exists.
    app.config.from_pyfile('config.py', silent=True)

    app.config['CRACKERJACK_VERSION'] = version.__version__

    # If we have passed any object on app creation (ie testing), override here.
    if config_class is not None:
        app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    crontab.init_app(app)

    from app.controllers.home import bp as home_bp
    app.register_blueprint(home_bp, url_prefix='/')

    from app.controllers.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.controllers.sessions import bp as sessions_bp
    app.register_blueprint(sessions_bp, url_prefix='/sessions')

    from app.controllers.install import bp as install_bp
    app.register_blueprint(install_bp, url_prefix='/install')

    from app.controllers.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    csrf.exempt(api_bp)

    from app.controllers.webpush import bp as webpush_bp
    app.register_blueprint(webpush_bp, url_prefix='/webpush')

    from app.controllers.modules import bp as modules_bp
    app.register_blueprint(modules_bp)

    from app.controllers.config import bp as config_bp
    app.register_blueprint(config_bp)

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

        def basename(path):
            return os.path.basename(path)

        return dict(setting_get=setting_get, user_setting_get=user_setting_get, template=template, basename=basename)

    @app.before_request
    def before_request():
        skip_session_update = False

        if '/static/' in request.path:
            # Exclude session updates for /static/ URLs
            skip_session_update = True
        elif skip_session_update is False and request.endpoint in app.view_functions:
            # Exclude session updates for views that have @dont_update_session (is status checked in sessions).
            view_function = app.view_functions[request.endpoint]
            skip_session_update = hasattr(view_function, '_dont_update_session')

        if skip_session_update is False:
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=20)
            session.modified = True

    @app.after_request
    def after_request(response):
        response.headers['Server'] = 'Windows 98'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html', error=error), 500

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', error=error), 404

    @crontab.job(minute="*/5")
    def cron():
        provider = Provider()
        cron = provider.cron()
        cron.run()

    return app


# This has to be at the bottom.
from app.lib.models import user, config, sessions, hashcat, api, system, webpush
