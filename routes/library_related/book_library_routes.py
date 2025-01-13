from bson import ObjectId
from flask import Blueprint, request, jsonify

from services.database import db_provider
from utils.flask_auth import login_required
from datetime import datetime

bp = Blueprint('book_library', __name__)


@bp.route('/libraries', methods=['GET'])
@login_required
def get_libraries(user_id: str):
    param_target_user_id = request.args.get('userId')

    if param_target_user_id is not None and not ObjectId.is_valid(param_target_user_id):
        return jsonify({'error': 'Invalid userId'}), 400

    def _convert_object_id_to_string(doc):
        doc['bookListId'] = str(doc['bookListId'])
        doc['authorId'] = str(doc['authorId'])
        return doc

    aggregation_pipeline = [{
        '$project': {
            '_id': 0,
            'bookListId': '$_id',
            'authorId': 1,
            'title': 1,
            'bookCount': {
                '$size': '$books'
            },
            'isPrivate': 1
        }
    }]

    if param_target_user_id is None:
        aggregation_pipeline.insert(0, {
            '$match': {
                'authorId': ObjectId(user_id)
            }
        })

        libraries = db_provider.col_book_libraries.aggregate(aggregation_pipeline)

        return jsonify({
            'libraries': list(map(_convert_object_id_to_string, libraries))
        }), 200

    aggregation_pipeline.insert(0, {
        '$match': {
            'authorId': ObjectId(param_target_user_id),
            'isPrivate': False
        }
    })

    libraries = db_provider.col_book_libraries.aggregate(aggregation_pipeline)

    return jsonify({
        'libraries': list(map(_convert_object_id_to_string, libraries))
    }), 200


@bp.route('/libraries/containData/<string:book_id>', methods=['GET'])
@login_required
def get_libraries_contain_data(user_id: str, book_id: str):
    if not ObjectId.is_valid(book_id):
        return jsonify({'error': 'Invalid bookId'}), 400

    aggregation_pipeline = [
        {
            '$match': {
                'authorId': ObjectId(user_id),
            }
        }, {
            '$project': {
                '_id': 0,
                'bookListId': '$_id',
                'authorId': 1,
                'title': 1,
                'books': 1,
                'isPrivate': 1
            }
        }
    ]

    libraries = db_provider.col_book_libraries.aggregate(aggregation_pipeline)

    def _convert_to_api_output(doc: dict):
        doc['bookListId'] = str(doc['bookListId'])
        doc['authorId'] = str(doc['authorId'])
        doc['bookCount'] = len(doc['books'])
        doc['containsBook'] = book_id in doc['books']

        doc.pop('books')

        return doc

    libraries = list(map(_convert_to_api_output, libraries))

    return jsonify({
        'datas': libraries
    }), 200


@bp.route('/libraries/<string:library_id>', methods=['GET'])
@login_required
def get_library(user_id: str, library_id: str):
    if not ObjectId.is_valid(library_id):
        return jsonify({'error': 'Invalid libraryId'}), 400

    aggregation_pipeline = [
        {
            '$match': {
                '_id': ObjectId(library_id)
            }
        }, {
            '$project': {
                '_id': 0,
                'bookListId': '$_id',
                'authorId': 1,
                'title': 1,
                'bookCount': {
                    '$size': '$books'
                },
                'isPrivate': 1
            }
        }
    ]

    library_results = list(db_provider.col_book_libraries.aggregate(aggregation_pipeline))

    if len(library_results) == 0:
        return jsonify({'error': 'No library found'}), 404

    library = library_results[0]

    if str(library["authorId"]) != user_id and library["isPrivate"]:
        return jsonify({'error': 'No library found'}), 404

    book_data_results = list(db_provider.col_book_libraries.aggregate([
        {
            '$match': {
                '_id': ObjectId(library_id)
            }
        }, {
            '$unwind': '$books'
        }, {
            '$lookup': {
                'from': 'rawBookDatas',
                'localField': 'books',
                'foreignField': '_id',
                'as': 'bookDetails'
            }
        }, {
            '$unwind': '$bookDetails'
        }, {
            '$project': {
                '_id': 0,
                'bookId': '$_id',
                'title': '$bookDetails.volumeInfo.title',
                'authors': '$bookDetails.volumeInfo.authors',
                'thumbnailUrl': '$bookDetails.volumeInfo.imageLinks.thumbnail'
            }
        }
    ]))

    library['books'] = book_data_results

    # Convert ObjectIds to strings
    library['bookListId'] = str(library['bookListId'])
    library['authorId'] = str(library['authorId'])

    for book in library['books']:
        book['bookId'] = str(book['bookId'])

    return jsonify({
        'library': library
    }), 200


@bp.route('/libraries', methods=['POST'])
@login_required
def create_library(user_id: str):
    data = request.json

    title = data.get('title')
    is_private = data.get('isPrivate')

    if None in [title, is_private]:
        return jsonify({'error': 'Parameters named authorId, title and isPrivate are required'}), 400

    if title == '_likedBooks':
        return jsonify({'error': 'Invalid library name'}), 400

    new_library = {
        'authorId': ObjectId(user_id),
        'title': title,
        'books': [],
        'isPrivate': is_private
    }

    result = db_provider.col_book_libraries.insert_one(new_library)

    if not is_private:
        user = db_provider.col_users.find_one({'_id': ObjectId(user_id)})

        db_provider.col_feed.insert_one({
            'issuerUserId': ObjectId(user_id),
            'issuerNameSurname': user['nameSurname'],
            'issuedAt': datetime.now(),
            'type': 'bookListPublish',
            'details': {
                'bookListId': result.inserted_id,
                'bookListName': title
            }
        })

    return jsonify({
        'libraryId': str(result.inserted_id)
    }), 201


@bp.route('/libraries/<string:library_id>', methods=['PATCH'])
@login_required
def update_library(user_id: str, library_id: str):
    if not ObjectId.is_valid(library_id):
        return jsonify({'error': 'Invalid libraryId'}), 400

    data = request.json

    title = data.get('title')
    is_private = data.get('isPrivate')

    if title is None and is_private is None:
        return jsonify({'error': 'At least one of title or isPrivate parameters are required'}), 400

    updated_fields = {}

    if title is not None:
        updated_fields['title'] = title

    if is_private is not None:
        updated_fields['isPrivate'] = is_private

    result = db_provider.col_book_libraries.update_one({
        '_id': ObjectId(library_id),
        'authorId': ObjectId(user_id)
    }, {
        '$set': updated_fields
    })

    if result.matched_count == 0:
        return jsonify({'error': 'No library found'}), 404

    if not is_private:
        user = db_provider.col_users.find_one({'_id': ObjectId(user_id)})

        db_provider.col_feed.insert_one({
            'issuerUserId': ObjectId(user_id),
            'issuerNameSurname': user['nameSurname'],
            'issuedAt': datetime.now(),
            'type': 'bookListPublish',
            'details': {
                'bookListId': result.inserted_id,
                'bookListName': title
            }
        })

    return jsonify({'message': 'Updated'}), 200


@bp.route('/libraries/<string:library_id>', methods=['DELETE'])
@login_required
def delete_library(user_id: str, library_id: str):
    if not ObjectId.is_valid(library_id):
        return jsonify({'error': 'Invalid libraryId'}), 400

    result = db_provider.col_book_libraries.delete_one({
        '_id': ObjectId(library_id),
        'authorId': ObjectId(user_id)
    })

    if result.deleted_count == 0:
        return jsonify({'error': 'No library found'}), 404

    return jsonify({'message': 'Deleted'}), 200


@bp.route('/libraries/<string:library_id>/books', methods=['POST'])
@login_required
def add_book_to_library(user_id: str, library_id: str):
    if not ObjectId.is_valid(library_id):
        return jsonify({'error': 'Invalid libraryId'}), 400

    data = request.json
    book_id = data.get('bookId')

    if not ObjectId.is_valid(book_id):
        return jsonify({'error': 'Invalid bookId'}), 400

    result = db_provider.col_book_libraries.update_one({
        '_id': ObjectId(library_id),
        'authorId': ObjectId(user_id)
    }, {
        '$addToSet': {
            'books': ObjectId(book_id)
        }
    })

    if result.matched_count == 0:
        return jsonify({'error': 'No library found'}), 404

    return jsonify({'message': 'Added'}), 200


@bp.route('/libraries/<string:library_id>/books', methods=['DELETE'])
@login_required
def remove_book_from_library(user_id: str, library_id: str):
    if not ObjectId.is_valid(library_id):
        return jsonify({'error': 'Invalid libraryId'}), 400

    data = request.json
    book_id = data.get('bookId')

    if not ObjectId.is_valid(book_id):
        return jsonify({'error': 'Invalid bookId'}), 400

    result = db_provider.col_book_libraries.update_one({
        '_id': ObjectId(library_id),
        'authorId': ObjectId(user_id)
    }, {
        '$pull': {
            'books': ObjectId(book_id)
        }
    })

    if result.matched_count == 0:
        return jsonify({'error': 'No library found'}), 404

    return jsonify({'message': 'Removed'}), 200
