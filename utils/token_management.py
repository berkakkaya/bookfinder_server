from datetime import datetime, timezone
from datetime import timedelta
from os import environ

import jwt

from models.tokens import UserToken, TokenType

_TOKEN_KEY = environ.get("TOKEN_KEY")

assert _TOKEN_KEY is not None, "TOKEN_KEY environment variable must be set"


def generate_refresh_token(user_id: str) -> str:
    """Generate a refresh token for the user

    This token is used to refresh the access token when it expires.
    The generated token will be valid for 30 days.

    Parameters
    ----------
    user_id: str
        The user id to generate the token for

    Returns
    -------
    str
        The generated refresh token
    """

    return jwt.encode({
        "user_id": user_id,
        "type": "refresh",
        "exp": datetime.now(tz=timezone.utc) + timedelta(days=30)
    }, _TOKEN_KEY, algorithm="HS256")


def generate_access_token(user_id: str) -> str:
    """Generate an access token for the user

    This token is used to authenticate the user for the API requests.
    The generated token will be valid for 1 hour.

    Parameters
    ----------
    user_id: str
        The user id to generate the token for

    Returns
    -------
    str
        The generated access token
    """

    return jwt.encode({
        "user_id": user_id,
        "type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1)
    }, _TOKEN_KEY, algorithm="HS256")


def validate_token(
        token: str,
        expected_token_type: TokenType | None = None
) -> UserToken | None:
    """Validate the token

    This function will validate the token and return the payload if the token is valid.
    If the token is invalid, it will return None.

    Parameters
    ----------
    token : str
        The token to validate
    expected_token_type : TokenType | None
        The expected token type, if None, any token type will be accepted

    Returns
    -------
    UserToken | None
        The payload of the token if the token is valid, otherwise None
    """

    try:
        decoded = jwt.decode(token, _TOKEN_KEY, algorithms=["HS256"])
        raw_token_type = decoded.get("type")
        token_type: TokenType | None = None

        if raw_token_type is None:
            return None

        if raw_token_type is not None:
            if raw_token_type == "access":
                token_type = TokenType.ACCESS
            elif raw_token_type == "refresh":
                token_type = TokenType.REFRESH

        if token_type is None:
            return None

        if expected_token_type is not None and token_type != expected_token_type:
            return None

        return UserToken(
            user_id=decoded.get("user_id"),
            token_type=token_type
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
