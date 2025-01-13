from flask import Flask, Blueprint

from routes.auth_management import logon_routes
from routes.auth_management import token_routes
from routes.book_data_related import book_data_fetching
from routes.recommendation_algorithm import book_recommendations
from routes.user_management import user_data_fetching
from routes.feed_related import feed_entries_management
from routes.library_related import book_tracking_routes
from routes.library_related import book_library_routes

blueprints: list[Blueprint] = [
    logon_routes.bp,
    token_routes.bp,
    book_recommendations.bp,
    book_data_fetching.bp,
    user_data_fetching.bp,
    feed_entries_management.bp,
    book_tracking_routes.bp,
    book_library_routes.bp,
]


def register_blueprints(app: Flask):
    for bp in blueprints:
        app.register_blueprint(bp)


__all__ = [
    "blueprints",
    "register_blueprints",
]
