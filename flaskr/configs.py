from os import environ


ALLOWED_IMAGE_EXTENSIONS = (
    "JPG",
    "JPEG",
    "PNG",
    "GIF",
    "SVG",
)


STORAGE_BUCKET_NAME = environ["GCP_STORAGE_BUCKET"]
