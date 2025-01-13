from bson import ObjectId
from flask import Blueprint, request, jsonify

from services.database import db_provider
from utils.flask_auth import login_required

bp = Blueprint('feed_entries_management', __name__)


@bp.route('/feed', methods=['GET'])
@login_required
def get_feed_entries(user_id: str):
    param_get_updates_from_others = request.args.get('getUpdatesFromOthers')

    def _convert_object_id_to_string(doc):
        doc['_id'] = str(doc['_id'])
        doc['issuerUserId'] = str(doc['issuerUserId'])
        doc['issuedAt'] = doc['issuedAt'].isoformat()

        if doc['type'] == 'bookListPublish':
            doc['details']['bookListId'] = str(doc['details']['bookListId'])

        return doc

    if param_get_updates_from_others == '1':
        feed_entries = db_provider.col_feed.find()

        return jsonify({
            "feed": list(map(_convert_object_id_to_string, feed_entries))
        }), 200

    user = db_provider.col_users.find_one({"_id": ObjectId(user_id)})

    if user is None:
        return jsonify({
            "message": "User not found"
        }), 500

    follow_list = user.get('followedUsers', [])
    follow_list = [ObjectId(user_id) for user_id in follow_list]

    feed_entries = db_provider.col_feed.find({
        "issuerUserId": {
            "$in": follow_list
        }
    })

    return jsonify({
        "feed": list(map(_convert_object_id_to_string, feed_entries))
    }), 200
