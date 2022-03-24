from firebase_admin import storage
from flask import current_app as app

from flaskr.configs import STORAGE_BUCKET_NAME


bucket = storage.bucket(name=STORAGE_BUCKET_NAME)
