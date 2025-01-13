from flask import Blueprint, request, jsonify
from pymongo.errors import DuplicateKeyError

from services.database import db_provider
from utils.pw_ops import verify_password, hash_password
from utils.token_management import generate_refresh_token, generate_access_token

bp = Blueprint("logon_routes", __name__)


@bp.route("/login", methods=["POST"])
def post_login_route():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    # If email or password are missing, return an error
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    db_user = db_provider.col_users.find_one({"email": email})

    # If user does not exist, return an unauthorized error
    if not db_user:
        return jsonify({"error": "Wrong email or password"}), 401

    # Check if password is correct
    is_pw_correct = verify_password(password, db_user["password"])

    # If password is incorrect, return an unauthorized error
    if not is_pw_correct:
        return jsonify({"error": "Wrong email or password"}), 401

    # Create a token for the user
    refresh_token = generate_refresh_token(str(db_user["_id"]))
    access_token = generate_access_token(str(db_user["_id"]))

    return jsonify({
        "refreshToken": refresh_token,
        "accessToken": access_token
    }), 200


@bp.route("/register", methods=["POST"])
def post_register_route():
    data = request.get_json()

    name_surname = data.get("nameSurname")
    email = data.get("email")
    password = data.get("password")

    # If user's name, email or password are missing, return an error
    if not name_surname or not email or not password:
        return jsonify({"error": "Missing name, email or password"}), 400

    # Try to insert the user into the database
    try:
        result = db_provider.col_users.insert_one({
            "nameSurname": name_surname,
            "email": email,
            "password": hash_password(password),
            "followedUsers": [],
        })
    except DuplicateKeyError:
        return jsonify({"error": "User with same email already exists"}), 409

    # Try to create liked books list for the user
    try:
        db_provider.col_book_libraries.insert_one({
            "authorId": result.inserted_id,
            "title": "_likedBooks",
            "books": [],
            "isPrivate": True
        })
    except DuplicateKeyError:
        return jsonify({"error": "User with same email already exists"}), 409

    # Get created user's id
    user_id = str(result.inserted_id)

    # Create a token for the user
    refresh_token = generate_refresh_token(user_id)
    access_token = generate_access_token(user_id)

    return jsonify({
        "refreshToken": refresh_token,
        "accessToken": access_token
    }), 201
