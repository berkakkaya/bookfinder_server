from bson import ObjectId
from bson.errors import InvalidId
from flask import Blueprint, jsonify, request

from services.database import db_provider
from utils.flask_auth import login_required

bp = Blueprint("user_data_fetching", __name__)


@bp.route("/users/<string:requested_user_id>", methods=["GET"])
@login_required
def get_user_details_route(user_id: str, requested_user_id: str):
    if requested_user_id == "me":
        requested_user_id = user_id

    try:
        result = db_provider.col_users.find_one(
            {"_id": ObjectId(requested_user_id)},
            projection={"_id": 0, "password": 0}
        )
    except InvalidId:
        return jsonify({"error": "Invalid user ID"}), 400

    if result is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "userId": requested_user_id,
        "email": result["email"],
        "nameSurname": result["nameSurname"],
        "followedUsers": result["followedUsers"],
    }), 200


@bp.route("/followingUsers", methods=["POST"])
@login_required
def follow_user_route(user_id: str):
    data = request.json

    if "userId" not in data:
        return jsonify({"error": "Missing 'userId' field"}), 400

    target_user_id = data["userId"]

    if not ObjectId.is_valid(target_user_id):
        return jsonify({"error": "Invalid user ID"}), 400

    if user_id == target_user_id:
        return jsonify({"error": "You cannot follow yourself"}), 400

    db_provider.col_users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"followedUsers": target_user_id}}
    )

    return jsonify({"message": "User followed successfully"}), 200


@bp.route("/followingUsers", methods=["DELETE"])
@login_required
def unfollow_user_route(user_id: str):
    data = request.json

    if "userId" not in data:
        return jsonify({"error": "Missing 'userId' field"}), 400

    target_user_id = data["userId"]

    if not ObjectId.is_valid(target_user_id):
        return jsonify({"error": "Invalid user ID"}), 400

    db_provider.col_users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"followedUsers": target_user_id}}
    )

    return jsonify({"message": "User unfollowed successfully"}), 200


@bp.route("/followStatus/<string:target_user_id>", methods=["GET"])
@login_required
def get_follow_status_route(user_id: str, target_user_id: str):
    if user_id == target_user_id:
        return jsonify({"error": "You cannot check follow status of yourself"}), 400

    result = db_provider.col_users.find_one(
        {"_id": ObjectId(user_id)},
        projection={"followedUsers": 1}
    )

    if result is None:
        return jsonify({"error": "User not found"}), 500

    followed_users = result.get("followedUsers", [])

    return jsonify({
        "isFollowing": target_user_id in followed_users,
    }), 200
