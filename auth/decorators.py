from functools import wraps

from flask import jsonify, request, current_app as app
from flask_api import status
import jwt

from flaskr.db import db
from users.models import User


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        try:
            bearer = request.headers["Authorization"]
            token = bearer.split()[1]
        except:
            pass

        if not token:
            return jsonify({"message": "Token is missing."}), status.HTTP_400_BAD_REQUEST
  
        user = __authenticate_user(token)
        
        if not user:
            return jsonify({"message": "Invalid token!"}), status.HTTP_401_UNAUTHORIZED
        else:
            # Returns the current logged in users contex to the routes
            return  f(user, *args, **kwargs)
  
    return decorated


def authenticate_if_present(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        user = None

        try:
            bearer = request.headers["Authorization"]
            token = bearer.split()[1]
        except:
            pass

        if token:
            user = __authenticate_user(token)
        
        # Returns the current logged in users contex to the routes
        return  f(user, *args, **kwargs)
  
    return decorated


def __authenticate_user(token: str) -> User:
    try:
        # Decoding the payload to fetch the stored details.
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_doc = db.collection(u"users").document(data["uid"]).get()
        return User.from_dict(user_doc.to_dict())
    except BaseException as e:
        print(e)
        return None
