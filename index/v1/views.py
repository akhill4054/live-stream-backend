from flask import Blueprint, jsonify, request
from flask_api import status
from auth.decorators import authenticate_if_present
from index.utils.helpers import create_live_stream_card
from firebase_admin import firestore

from flaskr.db import db
from users.models import User


index_bp = Blueprint('home', __name__, url_prefix="/home/api/v1")


@index_bp.route("/get-recommended-live-streams/", methods={"GET"})
@authenticate_if_present
def get_recommended_live_streams(user: User):
    after = request.args.get("after", None)
    count = request.args.get("count", None)
    count = int(count) if count else 5

    streamings_ref = db.collection(u"streamings").order_by(
        u'created_at', direction=firestore.Query.DESCENDING)
    query = streamings_ref

    if after:
        start_doc_snapshot = streamings_ref.document(after).get()
        query = query.start_after(start_doc_snapshot)

    query = query.limit(count)

    streaming_docs = query.stream()
    searched_live_streams = [create_live_stream_card(user, doc) for doc in streaming_docs]

    return jsonify(searched_live_streams), status.HTTP_200_OK


@index_bp.route("/search-live-streams/", methods={"GET"})
@authenticate_if_present
def search_live_streams(user: User):
    search_query = request.args.get("query", None)
    after = request.args.get("after", None)
    count = request.args.get("count", None)
    count = int(count) if count else 5
    
    is_live = request.args.get("is_live", None)
    is_popular = request.args.get("is_popular", None)

    streamings_ref = db.collection(u"streamings")
    query = streamings_ref

    if after:
        start_doc_snapshot = streamings_ref.document(after).get()
        query = query.start_after(start_doc_snapshot)

    if search_query != None and len(search_query) > 0:
        query = (query.where(u"title", u">=", search_query)
                    .where(u"title", u"<", search_query + "\uf8ff")
                )
    if is_live == True:
        query = query.where(u"is_live", u"==", is_live)
    if is_popular == True:
        query = query.where(u"is_popular", u">=", 0.8)

    query = query.limit(count)

    streaming_docs = query.stream()
    searched_live_streams = [create_live_stream_card(user, doc) for doc in streaming_docs]

    return jsonify(searched_live_streams), status.HTTP_200_OK
