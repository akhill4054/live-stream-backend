from os import stat
from flask_api import status
from flask import Blueprint, jsonify, request, json

from auth.decorators import authentication_required
from flaskr.configs import ALLOWED_IMAGE_EXTENSIONS
from users.models import User, UserProfile
from users.utils.profile_helpers import (
    is_username_already_exists, is_email_already_exists, is_phone_number_already_exists, is_valid_email,
    is_valid_phone_number
)
from flaskr.db import db
from utils.exceptions import InvalidRequestError
from utils.helpers import upload_image
from utils.response_helpers import get_invalid_request_response


users_bp = Blueprint("users", __name__, url_prefix="/users/api/v1")


@users_bp.route("/get-user-profile/", methods={"GET"})
@authentication_required
def get_user_profile(user: User):
    user_profile_doc_ref = db.collection(u"user_profiles").document(user.uid).get()

    user_profile_data = None

    if user_profile_doc_ref.exists:
        user_profile_data = {}
        user_profile_data.update(user.to_dict())
        user_profile_data.update(user_profile_doc_ref.to_dict())
    
    return jsonify({"user_profile": user_profile_data}), status.HTTP_200_OK


@users_bp.route("/update-user-profile/", methods={"POST"})
@authentication_required
def update_user_profile(user: User):
    def is_null_or_empty(s: str) -> bool: return s == None or len(s) == 0

    try:
        user_profile_data = json.loads(request.form["user_profile"])

        email = user_profile_data["email"]

        if is_null_or_empty(email):
            return get_invalid_request_response(message="Email cannot be empty.")
        elif is_valid_email(email):
            if user.email != email:
                if not is_email_already_exists(email):
                    user.email = email
                else:
                    raise InvalidRequestError(message=f"Email {email} already exists.")
        else:
            raise InvalidRequestError(message=f"Invalid email address.")

        username = user_profile_data["username"]

        if not is_valid_username(username):
            return get_invalid_request_response(message=f"Provided username is not valid.")
        elif user.username != username:
            if not is_username_already_exists(username):
                user.username = username
            else:
                raise InvalidRequestError(message=f"Username {username} already exists.")

        phone = user_profile_data.get("phone", None)

        if not is_null_or_empty(phone) and user.phone != phone:
            if is_valid_phone_number(phone):
                if not is_phone_number_already_exists(phone):
                    user.phone = phone
                else:
                    return jsonify({"message": f"Someone else is already using {phone}."}), status.HTTP_400_BAD_REQUEST
            else:
                return jsonify({"message": "Invalid phone number."}), status.HTTP_400_BAD_REQUEST

        name = user_profile_data.get("name", None)

        if not is_null_or_empty(name):
            user.name = name
        else:
            return jsonify({"message": "Please enter your name."}), status.HTTP_400_BAD_REQUEST

        # User profile.
        user_profile = None
        user_profile_doc = db.collection(
            u"user_profiles").document(user.uid).get()

        if user_profile_doc.exists:
            user_profile = UserProfile.from_dict(user_profile_doc.to_dict())
        else:
            user_profile = UserProfile()

        age = user_profile_data.get("age", None)

        if age != None:
            if age >= 12:
                user_profile.age = age
            else:
                return jsonify({"message": "You must be at least 12 years old to use this service."}), status.HTTP_400_BAD_REQUEST
        else:
            return jsonify({"message": "Please provide your age."}), status.HTTP_400_BAD_REQUEST

        profile_pic_file = request.files.get("profile_pic", None)
        if profile_pic_file:
            user_profile.pic_url = upload_image(profile_pic_file, f"profile_pics/{user.uid}")

        # Fields that the user is allowed to remove/make null.
        user_profile.sex = user_profile_data.get("sex", None)
        
        bio = user_profile_data.get("bio", None)
        if bio: bio = bio.strip()
        user_profile.bio = bio

        # Save user.
        db.collection(u"users").document(user.uid).set(user.to_dict())
        # Save user profile.
        db.collection(u"user_profiles").document(user.uid).set(user_profile.to_dict())

        response_profile_data = user.to_dict()
        response_profile_data.update(user_profile.to_dict())

        return jsonify({"user_profile": response_profile_data}), status.HTTP_200_OK
    except BaseException as e:
        if e is InvalidRequestError:
            return jsonify({"message": e.message}), status.HTTP_400_BAD_REQUEST
        else:
            return jsonify({"message": str(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR


@users_bp.route("/is-valid-username/", methods={"GET"})
@authentication_required
def is_valid_username(user: User):
    username = request.args.get("username", None)

    if not username:
        return jsonify({"message": "Must provide a username."}), status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        is_valid: bool = False
        message: str = None

        # TODO: Add regex to allow usernames only if they start with letters and cosist only letters, numbers, and underscore. 
        if len(username) < 5:
            message = "Username must be at least 5 characters long."
        elif len(username) > 12:
            message = "Username must be at most 12 charcters long."
        elif user.username != username and is_username_already_exists(username):
            message = f"Username '{username}' already exists, please pick a different username."
        else:
            is_valid = True
            message = f"'{username}' is good to go!"

        return jsonify({"is_valid": is_valid, "message": message}), status.HTTP_200_OK
