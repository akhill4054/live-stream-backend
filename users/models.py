class User(object):
    def __init__(self, uid, email=None, phone=None, username=None, name=None) -> None:
        self.uid = uid
        self.email = email
        self.phone = phone
        self.username = username
        self.name = name

    @staticmethod
    def from_dict(source):
        return User(
            uid=source["uid"],
            username=source.get("username", None),
            name=source.get("name", None),
            email=source.get("email", None),
            phone=source.get("phone", None),
        )

    def to_dict(self) -> dict:
        return {
            "uid": self.uid,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
        }


class UserProfile(object):
    def __init__(self, pic_url=None, age=None, sex=None, bio=None) -> None:
        self.pic_url = pic_url
        self.age = age
        self.sex = sex
        self.bio = bio

    @staticmethod
    def from_dict(source):
        return UserProfile(
            pic_url=source.get("pic_url", None),
            age=source.get("age", None),
            sex=source.get("sex", None),
            bio=source.get("bio", None),
        )

    def to_dict(self) -> dict:
        return {
            "pic_url": self.pic_url,
            "age": self.age,
            "sex": self.sex,
            "bio": self.bio,
        }


class UserPreferences(object):
    def __init__(self, liked_tags: list = []) -> None:
        self.liked_tags = liked_tags

    @staticmethod
    def from_dict(source):
        return UserPreferences(
            liked_tags=source["liked_tags"],
        )

    def to_dict(self) -> dict:
        return {
            "liked_tags": self.liked_tags,
        }
