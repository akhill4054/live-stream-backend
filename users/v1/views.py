from flask_api import status
from flask import Blueprint, jsonify, request

from auth.decorators import authentication_required
from users.models import User, UserProfile
from users.utils.profile_helpers import (
    is_username_already_exists, is_email_already_exists, is_phone_number_already_exists, is_valid_email,
    is_valid_phone_number
)
from flaskr.db import db


users_bp = Blueprint("users", __name__, url_prefix="/users/api/v1")


@users_bp.route("/update-user-profile/", methods={"POST"})
@authentication_required
def update_user_profile(user: User):
    user_profile_data = request.json.get("user_profile")

    if not user_profile_data:
        return jsonify({"message": "Invalid request."}), status.HTTP_400_BAD_REQUEST

    def helper_is_not_null_or_empty(string: str) -> bool:
        return string != None and len(string) > 0

    email = user_profile_data.get("email", None)

    if helper_is_not_null_or_empty(email):
        if is_valid_email(email):
            if user.email != email:
                if not is_email_already_exists(email):
                    user.email = email
                else:
                    return jsonify({"message": f"Email {email} already exists."}), status.HTTP_400_BAD_REQUEST
        else:
             return jsonify({"message": f"Invalid email address."}), status.HTTP_400_BAD_REQUEST
    else:
        return jsonify({"message": "Email is required in order to Sign In."}), status.HTTP_400_BAD_REQUEST
    
    username = user_profile_data.get("username", None)

    if helper_is_not_null_or_empty(username):
        if user.username != username:
            if not is_username_already_exists(username):
                user.username = username
            else:
                return jsonify({"message": f"Username {username} already exists."}), status.HTTP_400_BAD_REQUEST
    else:
        return jsonify({"message": "Username is required in order to create a profile."}), status.HTTP_400_BAD_REQUEST


    phone = user_profile_data.get("phone", None)

    if helper_is_not_null_or_empty(phone) and user.phone != phone:
        if is_valid_phone_number(phone):
            if not is_phone_number_already_exists(phone):
                user.phone = phone
            else:
                return jsonify({"message": f"Someone else is already using {phone}."}), status.HTTP_400_BAD_REQUEST
        else:
            return jsonify({"message": "Invalid phone number."}), status.HTTP_400_BAD_REQUEST

    name = user_profile_data.get("name", None)

    if helper_is_not_null_or_empty(name):
        user.name = name
    else:
        return jsonify({"message": "Please enter your name."}), status.HTTP_400_BAD_REQUEST

    # User profile.
    user_profile = None
    user_profile_doc = db.collection(u"user_profiles").document(user.uid).get()

    if user_profile_doc.exists:
        user_profile = UserProfile.from_dict(user_profile_doc.to_dict())
    else:
        user_profile = UserProfile()

    age = user_profile_data.get("age", None)

    if age != None:
        if age >= 12:
            user_profile.age = age
        else:
            return jsonify({"message": "You must be at least 12 years old to use this service."})
    else:
        return jsonify({"message": "Please provide your age."})

    # Fields that the user is allowed to remove/make null.
    user_profile.pic_url = user_profile_data.get("pic_url", None)
    user_profile.sex = user_profile_data.get("sex", None)
    user_profile.bio = user_profile_data.get("bio", None)

    # Save user.
    db.collection(u"users").document(user.uid).set(user.to_dict())
    # Save user profile.
    db.collection(u"user_profiles").document(user.uid).set(user_profile.to_dict())

    response_profile_data = user.to_dict()
    response_profile_data.update(user_profile.to_dict())

    return jsonify({"user_profile": response_profile_data}), status.HTTP_200_OK
