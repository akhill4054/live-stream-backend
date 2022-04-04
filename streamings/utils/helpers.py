from datetime import datetime

from streamings.models import Streaming
from werkzeug.datastructures import FileStorage

from users.models import User
from utils.exceptions import InvalidRequestError
from flaskr.db import db
from utils.helpers import upload_image


def save_scheduled_streaming(
    user: User, 
    streaming_details: dict, 
    thumbnail_image_file: FileStorage, 
    streaming_doc_id: str = None
):
    current_datetime = datetime.utcnow()
    scheduled_timestamp = streaming_details["scheduled_timestamp"]

    is_edit = streaming_doc_id != None

    if scheduled_timestamp < current_datetime.timestamp():
        raise InvalidRequestError(
            message="Can't edit a streaming which has already started/ended." if is_edit else "Can't schedule a streaming in the past."
        )

    streaming = Streaming(
        title=streaming_details["title"],
        desc=streaming_details["desc"],
        streamer_uid=user.uid,
        tags=streaming_details.get("tags", None),
        # TODO: Parse and save custom tags.
        # custom_tags=streaming_details.get("custom_tags", None),
        scheduled_datetime=scheduled_timestamp,
    )
    
    streaming_doc = None

    if not streaming_doc_id:
        streaming_doc_id = db.collection(u"streamings").document().id
    else:
        streaming_doc = db.collection(u"streamings").document(streaming_doc_id).get()
        if streaming_doc.exists:
            streaming_doc = streaming_doc.to_dict()
        else:
            raise InvalidRequestError(message=f"Streaming with id {streaming_doc_id} does not exist.")
    
    if thumbnail_image_file:
        # Upload thumbnail image.
        upload_result = upload_image(thumbnail_image_file, f"streaming-thumbanails/{streaming_doc_id}-{datetime.utcnow().timestamp()}")
        streaming.thumbnail_file_path = upload_result[0]
        streaming.thumbnail = upload_result[1]
    elif is_edit:
        streaming.thumbnail = streaming_doc["thumbnail"]
    else:
        raise InvalidRequestError(message="Must provide a thumbnail image file!")

    # Save scheduled streaming.
    db.collection(u"streamings").document(streaming_doc_id).set(streaming.to_dict(), merge = is_edit)
