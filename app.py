import base64
import json
import os

import firebase_admin
from firebase_admin import credentials
from flask import Flask


# Init firebase-admin.
if not firebase_admin._apps:
    firebase_app_credential = credentials.Certificate(json.loads(base64.b64decode(os.environ["GOOGLE_APPLICATION_CREDS_BASE64"])))
    default_app = firebase_admin.initialize_app(credential=firebase_app_credential)


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
from index.v1.views import index_bp
from auth.v1.views import auth_bp
from users.v1.views import users_bp
from streamings.v1.views import streamins_bp

app.register_blueprint(index_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(streamins_bp)
