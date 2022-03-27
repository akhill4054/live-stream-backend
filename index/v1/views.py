from flask import Blueprint, jsonify, request
from flask_api import status
from index.utils.helpers import create_live_stream_card

from flaskr.db import db


index_bp = Blueprint('home', __name__, url_prefix="/home/api/v1")


@index_bp.route("/search-live-streams/", methods={"GET"})
def search_live_streams():
    # TODO: Implement search bu query + filters.
    # search_query = request.args.get("query", None)
    after = request.args.get("after", None)
    count = request.args.get("count", None)
    count = int(count) if count else 10
    
    streamings_ref = db.collection(u"streamings")
    query = streamings_ref

    if after:
        start_doc_snapshot = streamings_ref.document(after).get()
        query = query.order_by(u"title").start_after(start_doc_snapshot)

    query = query.limit(count)

    streaming_docs = query.stream()
    searched_live_streams = [create_live_stream_card(doc) for doc in streaming_docs]

    return jsonify({
        "live_streams": searched_live_streams,
    }), status.HTTP_200_OK
