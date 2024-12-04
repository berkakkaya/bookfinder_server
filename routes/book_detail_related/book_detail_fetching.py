from flask import Blueprint, jsonify
from services.database import db_provider
from utils.flask_auth import login_required


bp = Blueprint("book_detail_related", __name__)


@bp.route("/books/<string:book_id>", methods=["GET"])
@login_required
def get_book_detail(book_id: str, user_id: str):
    # TODO: Return more proper data in the future
    result = db_provider.col_raw_book_datas.find_one({"id": book_id})

    if result is None:
        return jsonify({"message": "Book not found"}), 404

    def _convert_id_to_str(doc):
        doc["_id"] = str(doc["id"])
        doc["id"] = str(doc["id"])

        return doc

    result = _convert_id_to_str(result)

    return jsonify(result), 200
