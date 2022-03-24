import os
from os import environ

import firebase_admin
from firebase_admin import credentials
from flask import Flask


# Init firebase-admin.
cred = credentials.Certificate(environ["GOOGLE_APPLICATION_CREDENTIALS"])
default_app = firebase_admin.initialize_app(cred)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Setup configs.
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Import and register blueprints
    from auth.v1.views import auth_bp
    from users.v1.views import users_bp
    from streamings.v1.views import streamins_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(streamins_bp)

    return app
