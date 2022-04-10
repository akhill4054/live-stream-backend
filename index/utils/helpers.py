from flaskr.db import db
from streamings.models import Streaming
from users.models import User
from utils.datetime_helpers import get_utc_timestamp


def create_live_stream_card(user: User, streaming_doc) -> dict:
    streaming_obj = Streaming.from_dict(streaming_doc.to_dict())

    streaming_obj.is_live = streaming_obj.scheduled_datetime <= get_utc_timestamp()

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

    if user:
        streaming_doc_ref = db.collection(u"streamings").document(streaming_obj.id)
        liked_user_doc = streaming_doc_ref.collection(u"liked_users").document(user.uid).get()
        disliked_user_doc = streaming_doc_ref.collection(u"disliked_users").document(user.uid).get()

        streaming_obj_as_dict["is_liked"] = liked_user_doc.exists
        streaming_obj_as_dict["is_disliked"] = disliked_user_doc.exists

    return streaming_obj_as_dict
