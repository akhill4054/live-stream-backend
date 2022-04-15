from flask import Blueprint, jsonify, request, current_app as app
from flask_api import status
from firebase_admin import auth
import jwt

from auth.decorators import authentication_required
from flaskr.db import db
from users.models import User
from utils.datetime_helpers import get_utc_timestamp


auth_bp = Blueprint("auth", __name__, url_prefix="/auth/api/v1")


@auth_bp.route("/authenticate-user/", methods={"POST"})
def authenticate_user():
    token = request.json.get("token", None)

    if not token:
        return jsonify({"message": "Token missing."}), status.HTTP_400_BAD_REQUEST 

    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
        
        user_doc = db.collection(u"users").document(uid).get()

        if not user_doc.exists:
            name = decoded_token.get("name", None)
            email = decoded_token.get("email", None)
            pic_url = decoded_token.get("picture", None)
            phone = decoded_token.get("phone_number", None)

            user = User(uid=uid, name=name, email=email, phone=phone)

            # Create user.
            db.collection(u"users").document(uid).set(user.to_dict())
        else:
            user = User.from_dict(user_doc.to_dict())
    except BaseException as e:
        return jsonify({"message": str(e)}), status.HTTP_401_UNAUTHORIZED

    # Generate JWT token.
    jwt_token = jwt.encode({"uid": uid}, app.config["SECRET_KEY"])

    return jsonify({"token": jwt_token, "user": user.to_dict()}), status.HTTP_200_OK


@auth_bp.route("/test-authentication/", methods={"GET", "POST"})
@authentication_required
def test_authentication(user):
    for doc in db.collection(u"streamings").stream():
        db.collection(u"streamings").document(doc.id).set({"created_at": get_utc_timestamp()}, merge = True)

    return jsonify({"uid": user.uid}), status.HTTP_200_OK
