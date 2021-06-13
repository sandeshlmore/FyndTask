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
    def get(self):
        filters = eval(request.args.get('filters', {}))  ## {'genre':['Comedy', 'Drama']}
        page_no = int(request.args.get('page_no', 1))
        per_page = int(request.args.get('per_page', 10))
        search_string = eval(request.args.get('search_string', 'None'))
        sort = eval(request.args.get('sorting', 'None'))

        print('search_string')
        print(search_string)
        movies = get_movies(filters, search_string, sort, page_no, per_page)
        return make_response(
            jsonify({'status': API_SUCCESS_STATUS, 'message': 'MOVIES_RETRIEVED_SUCCESSFULLY', 'data': movies}),
            200)


    @jwt_required
    @check_admin_access
    def post(self):
        is_add = request.json.get('is_add', False)
        is_edit = request.json.get('is_edit', False)
        is_get = request.json.get('is_get', False)
        is_delete = request.json.get('is_delete', False)

        try:
            # has_admin_access = check_admin_access()
            # if not has_admin_access:
            #     return make_response(jsonify(
            #         {'status': API_SUCCESS_STATUS, 'message': 'ACTION_NOT_ALLOWED_TO_NON_ADMIN_USER'}), 200)
            if is_edit:
                movie_update = request.json.get('movie_update')
                movie_id = movie_update.get('_id') ##TODO: validate movie schema

                if (not isinstance(movie_id, str)) or (bson.objectid.ObjectId.is_valid(movie_id)):
                    return make_response(
                        jsonify({'status': API_SUCCESS_STATUS, 'message': 'INVALID_MOVIE_ID', '_id': movie_id}),
                        200)
                result = edit_movie(movie_id, movie_update)
                if result.raw_result.get('updatedExisting', False):
                    return make_response(jsonify(
                        {'status': API_SUCCESS_STATUS, 'message': 'MOVIE_EDITED_SUCCESSFULLY', '_id': movie_id}), 200)
                else:
                    return make_response(jsonify(
                        {'status': API_SUCCESS_STATUS, 'message': 'MOVIE_UPDATE_OPERATION_FAILED', '_id': movie_id}),
                        200)

            elif is_delete:
                movie_id = request.json.get('movie_id')

                if (not isinstance(movie_id, str)) or (bson.objectid.ObjectId.is_valid(movie_id)):
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
                movie = request.json.get('movie') ##TODO: validate movie schema
                if not isinstance(movie, dict):
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
                filters = request.json.get('filters', {})  ## {'genre':['Comedy', 'Drama']}
                page_no = request.json.get('page_no', 1)
                per_page = request.json.get('per_page', 10)
                search_string = request.json.get('search_string', None)
                sort = request.json.get('sorting', None)
                movies = get_movies(filters, search_string, sort, page_no, per_page)
                return make_response(
                    jsonify({'status': API_SUCCESS_STATUS, 'message': 'MOVIES_RETRIEVED_SUCCESSFULLY', 'data': movies}),
                    200)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return make_response(jsonify({'status': API_ERROR_STATUS, 'errors': str(e)}), 500)




api.add_resource(Movies, '/movies')

