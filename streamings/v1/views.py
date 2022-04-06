import hashlib
from random import randrange
from flask import Blueprint, jsonify, request, json
from flask_api import status

from auth.decorators import authenticate_if_present, authentication_required
from rtc.src.RtcTokenBuilder import Role_Attendee, Role_Publisher
from streamings.models import Streaming
from streamings.utils.helpers import save_scheduled_streaming
from users.models import User
from utils.datetime_helpers import get_utc_timestamp
from flaskr.db import db
from rtc.rtc_token import generate_rtc_token


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


@streamins_bp.route("/start-live-stream/", methods={"POST"})
@authentication_required
def start_live_stream(user: User):
    try:
        streaming_details = json.loads(request.form["streaming_details"])
        thumbnail_file = request.files["thumbnail"]

        streaming_details = save_scheduled_streaming(user, streaming_details, thumbnail_file, is_immedieate_scheduling=True)

        return jsonify({
            "message": "Streaming satarted.", 
            "streaming_details": streaming_details}
            ), status.HTTP_200_OK
    except BaseException as e:
        return jsonify({"message": str(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR


@streamins_bp.route("/watch-live-stream/", methods={"GET"})
@authenticate_if_present
def watch_live_stream_details(user: User):
    try:
        streaming_id = request.args["streaming_id"]
        streaming_doc = db.collection(u"streamings").document(streaming_id).get()
        streaming = Streaming.from_dict(streaming_doc.to_dict())
        
        ag_creds = None
        is_streamer = user != None and user.uid == streaming.streamer_uid

        streaming.is_live = streaming.scheduled_datetime <= get_utc_timestamp()
        
        if streaming.is_live:
            if not is_streamer:
                streaming.views += 1

                # Update view.
                db.collection(u"streamings").document(streaming_id).set({
                    "views": streaming.views,
                }, merge = True)

            if user:
                uid_md5 = hashlib.md5()
                uid_md5.update(user.uid.encode("utf-8"))
                uid = int(str(int(uid_md5.hexdigest(), 16))[1:10])
            else:
                uid = streaming.views

            user_role = Role_Publisher if is_streamer else Role_Attendee
            channel_name = streaming_doc.id

            ag_creds = {
                "channel_name": channel_name,
                "ag_uid": uid,
                "rtc_token": generate_rtc_token(uid=uid, channel_name=channel_name, role=user_role),
            }

        response_data = {
            "streaming_details": streaming.to_dict(),
            "is_streamer": is_streamer,
            "ag_creds": ag_creds,
        }

        return jsonify(response_data), status.HTTP_200_OK
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
    return {"s_timestamp": get_utc_timestamp()}
