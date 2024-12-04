from flask import Blueprint, request
from utils.token_management import validate_token, generate_access_token
from models.tokens import TokenType


bp = Blueprint("token_routes", __name__)


@bp.route("/token", methods=["POST"])
def get_new_access_token_route():
    # Extract the Authorization header
    auth_header = request.headers.get("Authorization")

    # Check if Authorization header is missing
    if not auth_header:
        return {"error": "Authorization header is missing"}, 400

    # Split the Authorization header
    auth_split = auth_header.split(" ")

    # Check if Authorization header contains 2 parts
    if len(auth_split) != 2:
        return {"error": "Authorization header is invalid"}, 400

    # Check if Authorization header is Bearer
    if auth_split[0] != "Bearer":
        return {"error": "Authorization header must be Bearer"}, 400

    # Extract refresh token
    refresh_token = auth_split[1]

    # Validate refresh token
    user = validate_token(
        token=refresh_token,
        expected_token_type=TokenType.REFRESH
    )

    # Check if refresh token is valid
    if not user:
        return {"error": "Invalid refresh token"}, 401

    # Refresh token
    access_token = generate_access_token(user.user_id)

    # Return newly created access token
    return {
        "accessToken": access_token,
    }, 201
