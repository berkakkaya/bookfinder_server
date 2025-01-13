from bson import ObjectId
from flask import Blueprint, request, jsonify

from services.database import db_provider
from utils.flask_auth import login_required

bp = Blueprint('book_tracking', __name__)


@bp.route('/bookTrackDatas', methods=['GET'])
@login_required
def get_book_track_datas(user_id: str):
    query_book_id = request.args.get('bookId')

    if query_book_id is not None and not ObjectId.is_valid(query_book_id):
        return jsonify({'error': 'Invalid bookId'}), 400

    aggregation_pipeline = [
        {
            '$lookup': {
                'from': 'rawBookDatas',
                'localField': 'bookId',
                'foreignField': '_id',
                'as': 'bookData'
            }
        }, {
            '$unwind': {
                'path': '$bookData',
                'preserveNullAndEmptyArrays': False
            }
        }, {
            '$project': {
                '_id': 0,
                'bookId': 1,
                'status': 1,
                'bookTitle': '$bookData.volumeInfo.title',
                'bookAuthors': '$bookData.volumeInfo.authors',
                'bookThumbnailUrl': '$bookData.volumeInfo.imageLinks.thumbnail'
            }
        }
    ]

    def _convert_object_id_to_string(doc):
        doc['bookId'] = str(doc['bookId'])
        return doc

    if query_book_id is not None:
        aggregation_pipeline.insert(0, {
            '$match': {
                'ownerUserId': ObjectId(user_id),
                'bookId': ObjectId(query_book_id)
            }
        })

        data = db_provider.col_book_tracking_statuses.aggregate(aggregation_pipeline)
        data_converted = list(map(_convert_object_id_to_string, data))

        if len(data_converted) == 0:
            return jsonify({'error': 'No data found'}), 404

        return jsonify({
            "data": data_converted[0]
        }), 200

    aggregation_pipeline.insert(0, {
        '$match': {
            'ownerUserId': ObjectId(user_id),
        },
    })

    datas = db_provider.col_book_tracking_statuses.aggregate(aggregation_pipeline)

    return jsonify({
        "datas": list(map(_convert_object_id_to_string, datas))
    }), 200


@bp.route('/bookTrackDatas', methods=['PATCH'])
@login_required
def patch_book_track_datas(user_id: str):
    data = request.json
    book_id = data.get('bookId')
    new_status = data.get('status')

    if not ObjectId.is_valid(book_id):
        return jsonify({'error': 'Invalid bookId'}), 400

    if new_status is not None:
        if new_status not in ['willRead', 'reading', 'completed', 'dropped']:
            return jsonify({'error': 'Invalid status argument'}), 400

        db_provider.col_book_tracking_statuses.update_one({
            'ownerUserId': ObjectId(user_id),
            'bookId': ObjectId(data.get('bookId'))
        }, {
            '$set': {'status': new_status}
        }, upsert=True)

        return jsonify({'message': 'Updated'}), 200

    db_provider.col_book_tracking_statuses.delete_one({
        'ownerUserId': ObjectId(user_id),
        'bookId': ObjectId(data.get('bookId'))
    })

    return jsonify({'message': 'Deleted'}), 200
