from flaskr.db import db
from streamings.models import Streaming


def create_live_stream_card(streaming_doc) -> dict:
    streaming_obj = Streaming.from_dict(streaming_doc.to_dict())
    streaming_obj_as_dict = streaming_obj.to_dict()

    # Get streamer info.
    streamer_user = db.collection(u"users").document(streaming_obj.streamer_uid).get().to_dict()
    streamer_profile = db.collection(u"user_profiles").document(streaming_obj.streamer_uid).get().to_dict()

    short_bio = streamer_profile.get("bio", None)
    if short_bio and len(short_bio) > 120:
        short_bio = short_bio[0:120]

    streaming_obj_as_dict["streamer"] = {
        "name": streamer_user["name"],
        "username": streamer_user["username"],
        "pic_url": streamer_profile.get("pic_url", None),
        "short_bio": short_bio,
        "followers_count": streamer_profile["followers_count"],
    }

    # Remove unnecessary data.
    streaming_obj_as_dict.pop("tags")

    return streaming_obj_as_dict
