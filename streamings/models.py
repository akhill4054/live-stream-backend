from datetime import datetime


class Streaming(object):
    def __init__(self, title: str, desc: str, streamer_uid: str, scheduled_datetime: datetime=None,
                 tags: list[str] = [], thumbnail: str = None, thumbnail_file_path: str = None, custom_tags: list[str] = [],
                 views: int = 0, is_live: bool = False, joined_people: int = 0, likes: int = 0,
                 dislikes: int = 0, popularity: int = 0) -> None:
        self.title = title
        self.desc = desc
        self.thumbnail_file_path = thumbnail_file_path
        self.thumbnail = thumbnail
        self.streamer_uid = streamer_uid
        self.scheduled_datetime = scheduled_datetime
        self.tags = tags
        self.custom_tags = custom_tags
        self.views = views
        self.is_live = is_live
        self.joined_people = joined_people
        self.likes = likes
        self.dislikes = dislikes
        self.poularity = popularity

    @staticmethod
    def from_dict(source: dict):
        return Streaming(
            title=source["title"],
            desc=source["desc"],
            thumbnail=source["thumbnail"],
            thumbnail_file_path=source["thumbnail_file_path"],
            streamer_uid=source["streamer_uid"],
            scheduled_datetime=source["scheduled_datetime"],
            tags=source["tags"],
            custom_tags=source["custom_tags"],
            views=source["views"],
            is_live=source["is_live"],
            joined_people=source["joined_people"],
            likes=source["likes"],
            dislikes=source["dislikes"],
            popularity=source.get("popularity", None),
        )

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "desc": self.desc,
            "thumbnail": self.thumbnail,
            "thumbnail_file_path": self.thumbnail_file_path,
            "streamer_uid": self.streamer_uid,
            "scheduled_datetime": self.scheduled_datetime,
            "tags": self.tags,
            "custom_tags": self.custom_tags,
            "views": self.views,
            "is_live": self.is_live,
            "joined_people": self.joined_people,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "poularity": self.poularity,
        }
