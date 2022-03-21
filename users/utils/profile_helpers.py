import re

from flaskr.db import db


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


def is_valid_email(email: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.fullmatch(regex, email)


def is_phone_number_already_exists(phone: str) -> bool:
    user_docs = db.collection(u"users").where(u"phone", u"==", phone).get()
    return len(user_docs) > 0


def is_email_already_exists(email: str) -> bool:
    user_docs = db.collection(u"users").where(u"email", u"==", email).get()
    return len(user_docs) > 0
