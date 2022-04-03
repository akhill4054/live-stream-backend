from flask_api import status


def get_invalid_request_response(message: str = None) -> tuple:
    return {"message": message}, status.HTTP_400_BAD_REQUEST
