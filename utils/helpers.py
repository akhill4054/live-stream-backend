from werkzeug.datastructures import FileStorage

from flaskr.configs import ALLOWED_IMAGE_EXTENSIONS
from flaskr.storage import bucket
from utils.exceptions import InvalidRequestError


def upload_image(image_file: FileStorage, path_without_extension: str) -> str:
    image_file_extension = image_file.filename.split(".")[1]

    if not image_file_extension.upper() in ALLOWED_IMAGE_EXTENSIONS:
        raise InvalidRequestError(
            message=f"Image type {image_file_extension.upper()} is not allowed.")

    thumbnail_blob = bucket.blob(f"{path_without_extension}.{image_file_extension}")
    thumbnail_blob.upload_from_file(image_file)
    thumbnail_blob.make_public()
    return thumbnail_blob.public_url
