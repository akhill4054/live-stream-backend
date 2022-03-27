from flaskr.db import db
from streamings.models import Streaming


def create_live_stream_card(streaming_doc) -> dict:
    streaming_obj = Streaming.from_dict(streaming_doc.to_dict())
    streaming_obj_as_dict = streaming_obj.to_dict()

    # Get streamer info.
    streamer_profile = db.collection(u"user_profiles").document(streaming_obj.streamer_uid).get().to_dict()

    short_bio = streamer_profile.get("bio", None)
    if short_bio and len(short_bio) > 120:
        short_bio = short_bio[0:120]

    streaming_obj_as_dict["streamer"] = {
        "pic_url": streamer_profile.get("pic_url", None),
        "short_bio": short_bio,
        "followers_count": 0,
    }

    # Remove unnecessary data.
    streaming_obj_as_dict.pop("custom_tags")
    streaming_obj_as_dict.pop("tags")

    return streaming_obj_as_dict
