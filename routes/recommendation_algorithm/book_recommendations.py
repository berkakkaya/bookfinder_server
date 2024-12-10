from flask import Blueprint, jsonify
from services.database import db_provider
from utils.flask_auth import login_required

bp = Blueprint("book_recommendations", __name__)


@bp.route("/recommendations", methods=["GET"])
@login_required
def get_recommendations(user_id: str):
    result = db_provider.col_raw_book_datas.aggregate([
        {
            "$sample": {
                "size": 10
            }
        },
        {
            "$match": {
                "volumeInfo.maturityRating": {
                    "$ne": "MATURE"
                }
            }
        },
        # {
        #     "$project": {
        #         "_id": 1,
        #         "id": 1,
        #         "title": "$volumeInfo.title",
        #         "subtitle": "$volumeInfo.subtitle",
        #         "thumbnail": "$volumeInfo.imageLinks.thumbnail"
        #     }
        # }
    ])
    
    def _convert_id_to_str(doc):
        doc["_id"] = str(doc["_id"])
        doc["id"] = str(doc["id"])

        return doc

    result = list(map(_convert_id_to_str, result))

    return jsonify(result), 200
