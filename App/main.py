import os
from flask import Flask, render_template, session
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from App.database import init_db, db
from App.config import load_config


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views, setup_admin
from App.models import User


def add_views(app):
    for view in views:
        app.register_blueprint(view)


def add_session_context(app):
    @app.context_processor
    def inject_session_user():
        user_id = session.get('user_id')
        if user_id:
            current_user = db.session.get(User, user_id)
            return dict(is_authenticated=True, current_user=current_user)
        return dict(is_authenticated=False, current_user=None)


def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    CORS(app, supports_credentials=True)
    add_auth_context(app)
    add_session_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    jwt = setup_jwt(app)
    setup_admin(app)
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401
    app.app_context().push()
    return app