#!/usr/bin/env python3

import atexit
import os

from flask import Flask
from flask_jsglue import JSGlue
from flask_security import Security, SQLAlchemyUserDatastore

from flask_app.core.db import db

from .core.models.docker import (Container, ContainerImage, Network,
                                 NetworkPreset)
from .core.models.user import Group, Role, User


def cleanup(app):
    if app.config["CLEANUP_BEFORE_AND_AFTER"]:
        with app.app_context():
            app.logger.info("Cleaning up containers and networks...")
            Container.cleanup()
            Network.cleanup()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(
        __name__)

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

    # cleanup any leftover containers, networks or files before starting or exiting
    atexit.register(cleanup,app=app)
    cleanup(app)

    # init flask-security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    with app.app_context():
        from flask_security.utils import hash_password

        try:
            admin_role = Role.create_role(
                name="admin",
                description="Privilidged role for administration purposes"
            )
            User.create_user(
                username="admin",
                password="123456",
                email="admin@test.local",
                roles=[admin_role]
            )

            User.create_user(
                username="test_user",
                password="123456",
                email="test@test.local",
                roles=[]
            )
        except Exception as err:
            pass

    # register blueprints
    register_blueprints(app)
    
    # init jsglue
    jsglue = JSGlue(app)

    return app

def register_blueprints(app):
    from flask_app.routes.api.docker import docker_api_bp
    from flask_app.routes.api.user import user_api_bp
    from flask_app.routes.views.index import index_bp
    from flask_app.routes.views.networks import networks_bp
    from flask_app.routes.views.users import users_bp
    blueprints = [
        docker_api_bp,
        user_api_bp,
        index_bp,
        networks_bp,
        users_bp
    ]
    
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
