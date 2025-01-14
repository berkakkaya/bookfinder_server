from bson import ObjectId

from services.database import db_provider
from random import shuffle

# Pool settings
SATURATION_LIMIT = 50
WEIGHT_LIMIT = 100
ADD_AMOUNT = 5
DECAY_AMOUNT = 1
DECAY_INTERVAL = 2

# Recommendation settings
RECOMMENDATION_SAMPLE_SIZE = 10
RECOMMENDATION_PERSONALIZED_MAX_PORTION = 0.8


def add_weight_to_category(user_id: str, book_id: str):
    pool_entry = db_provider.col_pools.find_one({"userId": (ObjectId(user_id))})

    if pool_entry is None:
        pool_entry = {
            "userId": ObjectId(user_id),
            "saturation": 1,
            "categories": {}
        }

    book = db_provider.col_raw_book_datas.find_one(
        {"_id": ObjectId(book_id)},
        projection={"category": 1}
    )

    if book is None:
        return

    category = book["category"]

    current_weight = pool_entry["categories"].get(category, 0)
    new_weight = current_weight + ADD_AMOUNT

    if new_weight > WEIGHT_LIMIT:
        new_weight = WEIGHT_LIMIT

    pool_entry["categories"][category] = new_weight

    pool_entry["saturation"] = pool_entry["saturation"] + 1

    if pool_entry["saturation"] >= SATURATION_LIMIT + DECAY_INTERVAL:
        for key in pool_entry["categories"]:
            decayed_weight = pool_entry["categories"][key] - DECAY_AMOUNT

            if decayed_weight < 0:
                decayed_weight = 0

            pool_entry["categories"][key] = decayed_weight

        pool_entry["saturation"] = SATURATION_LIMIT

    db_provider.col_pools.update_one({"userId": ObjectId(user_id)}, {"$set": pool_entry}, upsert=True)


def get_personalized_recommendations(user_id: str) -> list | None:
    pool_entry = db_provider.col_pools.find_one({"userId": ObjectId(user_id)})

    if pool_entry is None:
        return None

    # Check if user's category weights are all 0
    if sum(pool_entry["categories"].values()) == 0:
        return None

    # Calculate personalized portion
    saturation = pool_entry["saturation"]
    personalized_portion = min(saturation / SATURATION_LIMIT, RECOMMENDATION_PERSONALIZED_MAX_PORTION)

    # Take 3 categories with the highest weights
    categories: list[tuple[str, float]] = list(pool_entry["categories"].items())

    # Calculate total weight of the selected categories
    total_weight = sum(weight for _, weight in categories)

    # Calculate the book count for each category
    personalized_book_counts = {}

    for category, weight in categories:
        portion = weight / total_weight * personalized_portion
        book_count = int(RECOMMENDATION_SAMPLE_SIZE * portion)

        personalized_book_counts[category] = book_count

    # Calculate how many random books to take
    sum_personalized_book_counts = sum(personalized_book_counts.values())
    random_book_count = RECOMMENDATION_SAMPLE_SIZE - sum_personalized_book_counts

    # Prepare aggregation facets
    facets = {
        "randomSamples": [
            {
                "$sample": {"size": random_book_count}
            }
        ]
    }

    for category, book_count in personalized_book_counts.items():
        facets[category] = [
            {
                "$match": {
                    "category": category
                }
            },
            {
                "$sample": {"size": book_count}
            }
        ]

    # Aggregate books
    aggregation = [
        {
            "$match": {
                "volumeInfo.maturityRating": {
                    "$ne": "MATURE"
                },
                "volumeInfo.description": {
                    "$exists": True,
                    "$ne": ""
                }
            }
        },
        {
            "$facet": facets
        },
        {
            "$project": {
                "books": {
                    "$concatArrays": [
                        "$randomSamples",
                        *[
                            f"${category}" for category in personalized_book_counts
                        ]
                    ]
                }
            }
        },
        {
            '$unwind': {
                'path': '$books'
            }
        },
        {
            '$project': {
                'bookId': '$books._id',
                'title': '$books.volumeInfo.title',
                'authors': '$books.volumeInfo.authors',
                'description': '$books.volumeInfo.description',
                'thumbnail': '$books.volumeInfo.imageLinks.thumbnail'
            }
        }
    ]

    results = db_provider.col_raw_book_datas.aggregate(aggregation)

    return shuffle(list(results))
