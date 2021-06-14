from bson import ObjectId

from common.utils import check_admin_access
from master.views import db


def get_movies(filters, search_string=None, sort_on='imdb_score', ascending=1, page_no=1, per_page=0):
    start_index = (page_no - 1) * per_page
    end_index = per_page
    query_filters = {}
    if search_string:
        # search_string = str(search_string) if not isinstance(search_string, str) else search_string
        query_filters['name'] = {'$regex': search_string, '$options': 'i'}
    if 'genre' in filters:
        query_filters['genre'] = {'$in': filters['genre']}

    if not query_filters and filters:
        query_filters = filters
    # print('query_filters')
    # print(query_filters)
    movies = list(db.movies.find({**query_filters}).sort([(sort_on, ascending)]).skip(start_index).limit(end_index))
    total_results = db.movies.find({**query_filters}).count()

    return {'movies': movies, 'total_results': total_results}


@check_admin_access
def edit_movie(movie_id, movie):
    if '_id' in movie:
        del movie['_id']
    return db.movies.update_one({'_id': ObjectId(movie_id)}, {'$set': {**movie}})


@check_admin_access
def delete_movie(movie_id):
    return db.movies.delete_one({'_id': ObjectId(movie_id)})


@check_admin_access
def add_movie(movie):
    if '_id' in movie:
        del movie['_id']
    return db.movies.insert_one(movie)
