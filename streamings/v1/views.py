from datetime import datetime
from flask import Blueprint, jsonify, request, json
from flask_api import status

from auth.decorators import authentication_required
from streamings.utils.helpers import save_scheduled_streaming
from users.models import User


streamins_bp = Blueprint('streamings', __name__, url_prefix="/streamings/api/v1")


@streamins_bp.route("/schedule-live-stream/", methods={"POST"})
@authentication_required
def schedule_live_stream(user: User):
    try:
        streaming_details = json.loads(request.form["streaming_details"])
        thumbnail_file = request.files["thumbnail"]

        save_scheduled_streaming(user, streaming_details, thumbnail_file)

        return jsonify({"message": "Streaming scheduled."}), status.HTTP_200_OK
    except BaseException as e:
        return jsonify({"message": str(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR


@streamins_bp.route("/edit-scheduled-live-stream/", methods={"POST"})
@authentication_required
def edit_scheduled_live_stream(user: User):
    try:
        streaming_id = request.args["streaming_id"]

        streaming_details = json.loads(request.form["streaming_details"])
        thumbnail_file = request.files.get("thumbnail")

        save_scheduled_streaming(user, streaming_details, thumbnail_file, streaming_doc_id=streaming_id)

        return jsonify({"message": "Streaming modified."}), status.HTTP_200_OK
    except BaseException as e:
        return jsonify({"message": str(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR


@streamins_bp.route("/get-server-timestamp/", methods={"GET"})
def get_server_timestamp():
    return {"s_timestamp": datetime.utcnow().timestamp()}
