#!/usr/bin/env python3

import os

from flask import Flask
from flask_security import Security, SQLAlchemyUserDatastore

from flask_app.core.db import db

from .core.models.docker import Container, Network
from .core.models.user import Role, User


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        from .config import Config
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # init database
    db.init_app(app)
    with app.app_context():
        db.create_all()
    

    # init flask-security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    with app.app_context():
        from flask_security.utils import hash_password

        try:
            test_user = User(
                username=app.config['USERNAME'],
                password=hash_password(app.config['PASSWORD']),
                email='test@test.local',
                active=True
                )
            db.session.add(test_user)
            db.session.commit()
        except:
            pass

    # register blueprints
    register_blueprints(app)

    return app

def register_blueprints(app):
    from flask_app.routes.api.api import api_bp
    from flask_app.routes.api.auth import auth_bp
    from flask_app.routes.views.index import index_bp
    blueprints = [
        api_bp,
        auth_bp,
        index_bp
    ]


    for blueprint in blueprints:
        app.register_blueprint(blueprint)
