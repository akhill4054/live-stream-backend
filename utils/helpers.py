from werkzeug.datastructures import FileStorage

from flaskr.configs import ALLOWED_IMAGE_EXTENSIONS
from flaskr.storage import bucket
from utils.response_helpers import get_invalid_request_response


def upload_image(image_file: FileStorage, path_without_extension: str) -> tuple:
    split_filename = image_file.filename.split(".")
    image_file_extension = split_filename[len(split_filename) - 1]

    if not image_file_extension.upper() in ALLOWED_IMAGE_EXTENSIONS:
        raise Exception(f"Image type {image_file_extension.upper()} is not allowed.")

    full_file_path = f"{path_without_extension}.{image_file_extension}"

    thumbnail_blob = bucket.blob(full_file_path)
    thumbnail_blob.upload_from_file(image_file)
    thumbnail_blob.make_public()
    return (full_file_path, thumbnail_blob.public_url)
