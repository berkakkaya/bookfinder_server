from flask import Blueprint, jsonify, request

from models.book_categories import BookCategory
from services.database import db_provider
from utils import pool_ops
from utils.flask_auth import login_required

bp = Blueprint("book_recommendations", __name__)


@bp.route("/recommendations", methods=["GET"])
@login_required
def get_recommendations(user_id: str):
    param_category_filter = request.args.get("category")

    filters = {
        "volumeInfo.maturityRating": {
            "$ne": "MATURE"
        },
        "volumeInfo.description": {
            "$exists": True,
            "$ne": ""
        }
    }

    result = None

    if param_category_filter is not None:
        if param_category_filter not in list(map(str, BookCategory)):
            return jsonify({
                "error": f"Invalid category '{param_category_filter}'"
            }), 400

        filters["category"] = param_category_filter

        result = db_provider.col_raw_book_datas.aggregate([
            {
                "$match": filters
            },
            {
                "$sample": {
                    "size": 10
                }
            },
            {
                "$project": {
                    "bookId": "$_id",
                    "_id": 0,
                    "title": "$volumeInfo.title",
                    "authors": "$volumeInfo.authors",
                    "description": "$volumeInfo.description",
                    "thumbnail": "$volumeInfo.imageLinks.thumbnail"
                }
            }
        ])
    else:
        result = pool_ops.get_personalized_recommendations(user_id)

    if result is None:
        # Get random books
        result = db_provider.col_raw_book_datas.aggregate([
            {
                "$match": filters
            },
            {
                "$sample": {
                    "size": 10
                }
            },
            {
                "$project": {
                    "bookId": "$_id",
                    "_id": 0,
                    "title": "$volumeInfo.title",
                    "authors": "$volumeInfo.authors",
                    "description": "$volumeInfo.description",
                    "thumbnail": "$volumeInfo.imageLinks.thumbnail"
                }
            }
        ])

    def _convert_id_to_str(doc):
        doc["bookId"] = str(doc["bookId"])
        return doc

    result = list(map(_convert_id_to_str, result))

    return jsonify({
        "recommendations": result
    }), 200
