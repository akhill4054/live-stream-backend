from datetime import datetime

from streamings.models import Streaming
from werkzeug.datastructures import FileStorage

from users.models import User
from utils.datetime_helpers import get_utc_timestamp
from utils.exceptions import InvalidRequestError
from flaskr.db import db
from utils.helpers import upload_image


def save_scheduled_streaming(
    user: User, 
    streaming_details: dict, 
    thumbnail_image_file: FileStorage, 
    streaming_doc_id: str = None,
    is_immedieate_scheduling: bool = False
) -> dict:
    scheduled_timestamp = streaming_details.get("scheduled_timestamp", None)

    is_edit = streaming_doc_id != None
    
    if not streaming_doc_id:
        streaming_doc_id = db.collection(u"streamings").document().id
    else:
        streaming_doc = db.collection(u"streamings").document(streaming_doc_id).get()
        if streaming_doc.exists:
            streaming_doc = streaming_doc.to_dict()
        else:
            raise InvalidRequestError(message=f"Streaming with id {streaming_doc_id} does not exist.")


    if is_immedieate_scheduling:
        scheduled_timestamp = get_utc_timestamp()
    elif scheduled_timestamp == None:
        raise InvalidRequestError(message="Must provide a timestamp to schedule the live stream.")
    elif scheduled_timestamp < get_utc_timestamp():
        raise InvalidRequestError(
            message="Can't edit a streaming which has already started/ended." if is_edit else "Can't schedule a streaming in the past."
        )

    custom_tags = streaming_details.get("custom_tags", None)
    if custom_tags and len(custom_tags) > 0:
        custom_tags = custom_tags.split(",")
        temp = []
        for tag in custom_tags:
            if len(tag) > 0: temp.append(tag.strip())
        custom_tags = temp
    else:
        custom_tags = []

    streaming = Streaming(
        id=streaming_doc_id,
        title=streaming_details["title"],
        desc=streaming_details["desc"],
        streamer_uid=user.uid,
        tags=streaming_details.get("tags", None),
        custom_tags=custom_tags,
        scheduled_datetime=scheduled_timestamp,
        is_live=scheduled_timestamp <= get_utc_timestamp(),
    )
    
    streaming_doc = None
    
    if thumbnail_image_file:
        # Upload thumbnail image.
        upload_result = upload_image(thumbnail_image_file, f"streaming-thumbanails/{streaming_doc_id}-{datetime.utcnow().timestamp()}")
        streaming.thumbnail_file_path = upload_result[0]
        streaming.thumbnail = upload_result[1]
    elif is_edit:
        streaming.thumbnail = streaming_doc["thumbnail"]
    else:
        raise InvalidRequestError(message="Must provide a thumbnail image file!")

    streaming_as_dict = streaming.to_dict()
    streaming_as_dict["id"] = streaming_doc_id

    # Save scheduled streaming.
    db.collection(u"streamings").document(streaming_doc_id).set(streaming_as_dict, merge = is_edit)

    return streaming_as_dict
