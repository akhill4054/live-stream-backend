import re

from flaskr.db import db
from users.models import User


def is_username_already_exists(phone: str) -> bool:
    user_docs = db.collection(u"users").where(u"username", u"==", phone).get()
    return len(user_docs) > 0


def is_valid_phone_number(phone: str) -> bool:
    if phone == None or len(phone) != 10:
        return False
    elif phone.startswith("0") or phone.startswith("+"):
        return False
    else:
        return True


def is_valid_username(user: User, username: str) -> tuple:
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

    return (is_valid, message)


def is_valid_email(email: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(regex, email)


def is_phone_number_already_exists(phone: str) -> bool:
    user_docs = db.collection(u"users").where(u"phone", u"==", phone).get()
    return len(user_docs) > 0


def is_email_already_exists(email: str) -> bool:
    user_docs = db.collection(u"users").where(u"email", u"==", email).get()
    return len(user_docs) > 0
