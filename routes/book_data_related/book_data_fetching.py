from bson import ObjectId
from bson.errors import InvalidId
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
                "bookId": "$_id",
                "_id": 0,
                "title": "$volumeInfo.title",
                "thumbnail": "$volumeInfo.imageLinks.thumbnail"
            }
        }
    ])

    def _convert_results_to_api_output(doc):
        doc["bookId"] = str(doc["bookId"])
        return doc

    results = list(map(_convert_results_to_api_output, results))

    if len(results) == 0:
        return jsonify({"error": "No books found"}), 404

    return jsonify({
        "searchResults": results
    }), 200


@bp.route("/books/<string:book_id>", methods=["GET"])
@login_required
def get_book_details_route(book_id: str, user_id: str):
    try:
        result = db_provider.col_raw_book_datas.find_one({"_id": ObjectId(book_id)})
    except InvalidId:
        return jsonify({"error": "Invalid book ID"}), 400

    if result is None:
        return jsonify({"error": "Book not found"}), 404

    return jsonify({
        "bookId": str(result["_id"]),
        "title": result["volumeInfo"]["title"],
        "authors": result["volumeInfo"]["authors"],
        "description": result["volumeInfo"].get("description"),
        "thumbnail": result["volumeInfo"]["imageLinks"]["thumbnail"],
        "identifiers": result["volumeInfo"].get("industryIdentifiers", []),
    }), 200
