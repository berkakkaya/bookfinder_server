from flask import Flask, Blueprint

from routes.auth_management import logon_routes
from routes.auth_management import token_routes
from routes.book_data_related import book_data_fetching
from routes.recommendation_algorithm import book_recommendations

blueprints: list[Blueprint] = [
    logon_routes.bp,
    token_routes.bp,
    book_recommendations.bp,
    book_data_fetching.bp,
]


def register_blueprints(app: Flask):
    for bp in blueprints:
        app.register_blueprint(bp)


__all__ = [
    "blueprints",
    "register_blueprints",
]
