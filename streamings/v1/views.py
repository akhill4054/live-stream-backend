import hashlib
from random import randrange
from flask import Blueprint, jsonify, request, json
from flask_api import status

from auth.decorators import authenticate_if_present, authentication_required
from index.utils.helpers import create_live_stream_card
from rtc.src.RtcTokenBuilder import Role_Attendee, Role_Publisher
from streamings.models import Streaming
from streamings.utils.helpers import save_scheduled_streaming
from users.models import User
from utils.datetime_helpers import get_utc_timestamp
from flaskr.db import db
from rtc.rtc_token import generate_rtc_token, generate_rtm_token


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
        streaming_doc_ref = db.collection(u"streamings").document(streaming_id)
        streaming_doc = streaming_doc_ref.get()
        streaming = create_live_stream_card(user, streaming_doc)
        
        ag_creds = None
        is_streamer = user != None and user.uid == streaming["streamer_uid"]
        
        if streaming["is_live"]:
            if not is_streamer:
                if user:
                    user_in_viewed_users = streaming_doc_ref.collection(u"viewed_users").document(user.uid).get()
                    if not user_in_viewed_users.exists:
                        streaming_doc_ref.collection(u"viewed_users").document(user.uid).set({
                            "uid": user.uid,
                            "created_at": get_utc_timestamp(),
                        })
                        streaming["views"] += 1
                else:
                    streaming["views"] += 1

                # Update view.
                db.collection(u"streamings").document(streaming_id).set({
                    "views": streaming["views"],
                }, merge = True)

            if user:
                uid_md5 = hashlib.md5()
                uid_md5.update(user.uid.encode("utf-8"))
                uid = int(str(int(uid_md5.hexdigest(), 16))[1:10])
            else:
                uid = streaming["views"]

            user_role = Role_Publisher if is_streamer else Role_Attendee
            channel_name = streaming_doc.id

            ag_creds = {
                "channel_name": channel_name,
                "ag_uid": uid,
                "rtc_token": generate_rtc_token(uid=uid, channel_name=channel_name, role=user_role),
                "rtm_token": generate_rtm_token(uid=uid),
            }

        response_data = {
            "streaming_details": streaming,
            "is_streamer": is_streamer,
            "ag_creds": ag_creds,
        }

        return jsonify(response_data), status.HTTP_200_OK
    except BaseException as e:
        return jsonify({"message": str(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR


@streamins_bp.route("/like-live-stream/", methods={"POST"})
@authentication_required
def like_live_stream(user: User):
    try:
        streaming_id = request.args["streaming_id"]
        streaming_doc_ref = db.collection(u"streamings").document(streaming_id)
        streaming_doc_as_dict = streaming_doc_ref.get().to_dict()

        liked_users_ref = streaming_doc_ref.collection(u"liked_users")
        liked_user_doc_ref = liked_users_ref.document(user.uid)
        liked_user_doc = liked_user_doc_ref.get()

        is_liked = False
        updated_likes_count = streaming_doc_as_dict["likes"]
        updated_dislikes_count = streaming_doc_as_dict["dislikes"]

        user_profile_likes_ref = db.collection(u"user_profiles").document(user.uid).collection("liked_streamings")

        if not liked_user_doc.exists:
            streaming_doc_ref.collection(u"liked_users").document(user.uid).set({
                "uid": user.uid,
                "username": user.username,
            })
            user_profile_likes_ref.document(streaming_id).set({
                "streaming_id": streaming_id,
                "crated_at": get_utc_timestamp(),
            })
            updated_likes_count += 1
            is_liked = True

            disliked_user_doc_ref = streaming_doc_ref.collection(u"disliked_users").document(user.uid)
            disliked_user_doc = liked_user_doc_ref.get()

            if disliked_user_doc.exists:
                disliked_user_doc_ref.delete()
                updated_dislikes_count -= 1
        else:
            user_profile_likes_ref.document(streaming_id).delete()
            liked_user_doc_ref.delete()
            updated_likes_count -= 1
        
        streaming_doc_ref.set({
            "likes": updated_likes_count,
            "dislikes": updated_dislikes_count,    
        }, merge = True)

        return jsonify({
            "message": "Added to likes." if is_liked else "Removed from likes.",
            "likes": updated_likes_count, 
            "dislikes": updated_dislikes_count,
        }), status.HTTP_200_OK
    except BaseException as e:
        return jsonify({"message": str(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR


@streamins_bp.route("/dislike-live-stream/", methods={"POST"})
@authentication_required
def dislike_live_stream(user: User):
    try:
        streaming_id = request.args["streaming_id"]
        streaming_doc_ref = db.collection(u"streamings").document(streaming_id)
        streaming_doc_as_dict = streaming_doc_ref.get().to_dict()

        is_disliked = False
        updated_likes_count = streaming_doc_as_dict["likes"]
        updated_dislikes_count = streaming_doc_as_dict["dislikes"]

        disliked_user_doc_ref = db.collection(u"streamings").document(streaming_id).collection("disliked_users").document(user.uid)
        disliked_user_doc = disliked_user_doc_ref.get()

        if not disliked_user_doc.exists:
            streaming_doc_ref.collection(u"disliked_users").document(user.uid).set({
                "uid": user.uid,
                "username": user.username,
            })
            updated_dislikes_count += 1
            is_disliked = True

            liked_user_doc_ref = streaming_doc_ref.collection(u"liked_users").document(user.uid)
            liked_user_doc = liked_user_doc_ref.get()

            if liked_user_doc.exists:
                user_profile_likes_ref = db.collection(u"user_profiles").document(user.uid).collection("liked_streamings")
                user_profile_likes_ref.document(streaming_id).delete()
                liked_user_doc_ref.delete()
                updated_likes_count -= 1
        else:
            disliked_user_doc_ref.delete()
            updated_dislikes_count -= 1
        
        streaming_doc_ref.set({
            "likes": updated_dislikes_count,
            "dislikes": updated_dislikes_count,
        }, merge = True)

        return jsonify({
            "message": "Disliked video." if is_disliked else "Removed from dislikes.",
            "likes": updated_likes_count,
            "dislikes": updated_dislikes_count,
        }), status.HTTP_200_OK
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


@streamins_bp.route("/end-live-stream/", methods={"POST"})
def end_live_stream():
    try:
        streaming_id = request.args["streaming_id"]

        # Delete live stream.
        db.collection(u"streamings").document(streaming_id).delete()

        return jsonify({"message": "Streaming deleted."}), status.HTTP_200_OK
    except BaseException as e:
        return jsonify({"message": str(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR
    

@streamins_bp.route("/get-server-timestamp/", methods={"GET"})
def get_server_timestamp():
    return {"s_timestamp": get_utc_timestamp()}
