from flask import Blueprint, jsonify, request
from services.database import db_provider
from utils.flask_auth import login_required


bp = Blueprint("book_data_related", __name__)


@bp.route("/bookSearch", methods=["GET"])
@login_required
def search_books_route(user_id: str):
    search_query = request.args.get("q")

    if not search_query:
        return jsonify({"error": "Query parameter \"q\" is missing"}), 400

    results = db_provider.col_raw_book_datas.aggregate([
        {
            "$search": {
                "index": "default",
                "text": {
                    "query": search_query,
                    "path": "volumeInfo.title"
                }
            }
        },
        {
            "$limit": 5
        },
        {
            "$project": {
                "_id": 1,
                "id": 1,
                "title": "$volumeInfo.title",
            }
        }
    ])

    def _convert_id_to_str(doc):
        doc["_id"] = str(doc["_id"])
        doc["id"] = str(doc["id"])

        return doc

    results = list(map(_convert_id_to_str, results))

    if len(results) == 0:
        return jsonify({"error": "No books found"}), 404

    return jsonify(results), 200


@bp.route("/books/<string:book_id>", methods=["GET"])
@login_required
def get_book_details_route(book_id: str, user_id: str):
    # TODO: Return more proper data in the future
    result = db_provider.col_raw_book_datas.find_one({"id": book_id})

    if result is None:
        return jsonify({"error": "Book not found"}), 404

    def _convert_id_to_str(doc):
        doc["_id"] = str(doc["_id"])
        doc["id"] = str(doc["id"])

        return doc

    result = _convert_id_to_str(result)

    return jsonify(result), 200
