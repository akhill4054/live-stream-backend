from functools import wraps

from flask import jsonify, request, current_app as app
from flask_api import status
import jwt

from flaskr.db import db
from users.models import User


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        bearer = request.headers.get("Authorization", None)
        token = None
        try:
            token = bearer.split()[1]
        except:
            pass

        if not token:
            return jsonify({"message": "Token is missing."}), status.HTTP_400_BAD_REQUEST
  
        try:
            # Decoding the payload to fetch the stored details.
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_doc = db.collection(u"users").document(data["uid"]).get()
            user = User.from_dict(user_doc.to_dict())
        except BaseException as e:
            print(e)
            return jsonify({"message": "Invalid token!"}), status.HTTP_401_UNAUTHORIZED
        # Returns the current logged in users contex to the routes
        return  f(user, *args, **kwargs)
  
    return decorated
