#!/usr/bin/env python3

import os

from flask import Flask

from flask_app.core.db import db


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

    # register blueprints
    register_blueprints(app)

    return app

def register_blueprints(app):
    from flask_app.routes.api.api import api_bp
    from flask_app.routes.api.auth import auth_bp
    blueprints = [
        api_bp,
        auth_bp
    ]


    for blueprint in blueprints:
        app.register_blueprint(blueprint)
