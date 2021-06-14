import bson
from bson import ObjectId
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from common.constants import API_ERROR_STATUS, API_SUCCESS_STATUS
from common.utils import check_admin_access
from master.views import api
from movies.controller import get_movies, edit_movie, delete_movie, add_movie

movies_blueprint = Blueprint('movies_blueprint', __name__)


class Movies(Resource):
    '''
        Provides CRUD operations on movies
    '''

    def get(self):
        '''
            search_string: Search movie by name (case insensitive and returns records with partial matches)
            page_no: current page number defaults to 1
            per_page: maximum records per page defaults to 10 records  [set to 0 for retrieving all records]
            sort_on: 'imdb_score'
            ascending: 1 or -1 (for descending)
        '''
        try:
            page_no = int(request.args.get('page_no', 1))
            per_page = int(request.args.get('per_page', 10))
            search_string = request.args.get('search_string', None)
            sort_on = request.args.get('sort_on', 'imdb_score')
            ascending = eval(request.args.get('ascending', 1))
            filters = {}
            movies = get_movies(filters, search_string, sort_on, ascending, page_no, per_page)
            return make_response(
                jsonify({'status': API_SUCCESS_STATUS, 'message': 'MOVIES_RETRIEVED_SUCCESSFULLY', 'data': movies}),
                200)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return make_response(jsonify({'status': API_ERROR_STATUS, 'errors': str(e)}), 500)


    # @jwt_required
    def post(self):
        try:
            is_add = request.json.get('is_add', False)
            is_edit = request.json.get('is_edit', False)
            is_get = request.json.get('is_get', False) ##I like to use POST for everything!
            is_delete = request.json.get('is_delete', False)

            # has_admin_access = check_admin_access()
            # if not has_admin_access:
            #     return make_response(jsonify(
            #         {'status': API_SUCCESS_STATUS, 'message': 'ACTION_NOT_ALLOWED_TO_NON_ADMIN_USER'}), 200)
            if is_edit:
                '''
                    ##Edit movie
                    movie: dictionary object with '_id' field of type string(24-bytes long) mandatory
                '''
                movie_update = request.json.get('movie') #movie object
                movie_id = movie_update.get('_id') ##TODO: validate movie schema

                if not isinstance(movie_id, str) or not bson.objectid.ObjectId.is_valid(movie_id):
                    return make_response(
                        jsonify({'status': API_SUCCESS_STATUS, 'message': 'INVALID_MOVIE_ID'}),
                        200)
                result = edit_movie(movie_id, movie_update)
                if result.raw_result.get('updatedExisting', False):
                    return make_response(jsonify(
                        {'status': API_SUCCESS_STATUS, 'message': 'MOVIE_EDITED_SUCCESSFULLY'}), 200)
                else:
                    return make_response(jsonify(
                        {'status': API_SUCCESS_STATUS, 'message': 'MOVIE_UPDATE_OPERATION_FAILED'}),
                        200)

            elif is_delete:
                '''
                    #delete movie  (HARD DELETE)
                    movie_id: string(24-bytes long)
                '''
                movie_id = request.json.get('movie_id')

                if (not isinstance(movie_id, str)) or (not bson.objectid.ObjectId.is_valid(movie_id)):
                    return make_response(
                        jsonify({'status': API_SUCCESS_STATUS, 'message': 'INVALID_MOVIE_ID', '_id': movie_id}),
                        200)
                result = delete_movie(movie_id)
                if result.raw_result.get('n') == 1:
                    return make_response(jsonify(
                        {'status': API_SUCCESS_STATUS, 'message': 'MOVIE_DELETED_SUCCESSFULLY', '_id': movie_id}), 200)
                else:
                    return make_response(jsonify(
                        {'status': API_SUCCESS_STATUS, 'message': 'MOVIE_DELETE_OPERATION_FAILED', '_id': movie_id}),
                        200)

            elif is_add:
                '''
                    #Add new movie
                    movie: dictionary object with 'name' field mandatory
                '''
                movie = request.json.get('movie') ##TODO: validate movie schema

                if not isinstance(movie, dict) or 'name' not in movie or not bool(movie['name']):
                    return make_response(
                        jsonify({'status': API_SUCCESS_STATUS, 'message': 'INVALID_MOVIE_SCHEMA', '_id': movie}),
                        200)

                result = add_movie(movie)
                movie = get_movies(filters={'_id': ObjectId(result.inserted_id)})
                if movie:
                    return make_response(
                        jsonify({'status': API_SUCCESS_STATUS, 'message': 'MOVIE_ADDED_SUCCESSFULLY', 'data': movie}),
                        200)
                else:
                    return make_response(jsonify(
                        {'status': API_SUCCESS_STATUS, 'message': 'MOVIE_INSERT_OPERATION_FAILED', 'data': movie}), 200)

            elif is_get:
                '''
                    search_string: Search movie by name (case insensitive and returns records with partial matches)
                    filters: Filter movie by genre, director, ratings, etc.  e.g. {'genre':['Comedy', 'Drama']}
                    page_no: current page number defaults to 1
                    per_page: maximum records per page defaults to 10 records  [set to 0 for retrieving all records]
                    sort_on: defaults to field 'imdb_score' 
                    ascending: 1 or -1 (for descending)
                '''
                filters = request.json.get('filters', {})  ## {'genre':['Comedy', 'Drama']} key-value pair where values must be wrap in list
                page_no = request.json.get('page_no', 1)
                per_page = request.json.get('per_page', 10)
                search_string = request.json.get('search_string', None)
                sort_on = request.json.get('sort_on', 'imdb_score')
                ascending = request.json.get('ascending', 1)
                movies = get_movies(filters, search_string, sort_on, ascending, page_no, per_page)
                return make_response(
                    jsonify({'status': API_SUCCESS_STATUS, 'message': 'MOVIES_RETRIEVED_SUCCESSFULLY', 'data': movies}),
                    200)

        except Exception as e:
            # import traceback
            # traceback.print_exc()
            return make_response(jsonify({'status': API_ERROR_STATUS, 'errors': str(e)}), 500)




api.add_resource(Movies, '/movies')

