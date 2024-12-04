from flask import request
from functools import wraps
from utils.token_management import validate_token
from models.tokens import TokenType


def login_required(f):
    """Decorator function to check if the user is logged in or not.

        If token check fails, it returns a ``401`` error.
        Else, it resumes the handling of the request.

        Also, ``user_id`` parameter is passed to the function if token check is successful.
        You can check who the user is by using this parameter.

        Here is an example of how you can use this decorator:

        ```python
        @app.route("/protected", methods=["GET"])
        @login_required # <-- Use the decorator here
        def protected_route(user_id: str):
            return {
                "message": f"Hello, user with id {user_id}!"
            }, 200
        ```

        Parameters
        ----------
        f : function
            The function that handles the request

        Returns
        -------
        function
            The function that handles the request with the token check implemented
        """

    @wraps(f)
    def controller_function(*args, **kwargs):
        # Fetch the Authorization header from the request
        authorization = request.headers.get("Authorization")

        # If the Authorization header is missing, return a 400 error
        if authorization is None:
            return {
                "message": "Authorization header is missing"
            }, 401

        # Split the Authorization header into two parts
        authorization = authorization.split(" ")

        # If the Authorization format is not Bearer, return a 400 error
        if len(authorization) != 2 or authorization[0] != "Bearer":
            return {
                "message": "Invalid authorization header"
            }, 401

        # Extract the access token from the Authorization header
        access_token = authorization[1]

        # Validate the access token and get the user id
        result = validate_token(
            token=access_token,
            expected_token_type=TokenType.ACCESS
        )

        if result is None:
            return {
                "message": "Invalid access token"
            }, 401

        # All checks have been passed, continue operating normally
        return f(*args, **kwargs, user_id=result.user_id)

    return controller_function
