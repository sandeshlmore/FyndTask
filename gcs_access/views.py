from importlib.resources import Resource
from flask import request, make_response, jsonify

from common.constants import API_SUCCESS_STATUS, API_ERROR_STATUS
from gcs_access.controller import generate_signed_url

import traceback
from common.exceptions import APIError
from master.views import app, api
from google.cloud import storage


class CustomObjectSignedUrl(Resource):
    def post(self):
        bucket_name = request.json.get('bucket_name', 'test-bucket0425')
        object_name = request.json.get('object_name', 'add_item (1).xlsx')
        expiration = request.json.get('expiration', 120)
        try:
            url = generate_signed_url(bucket_name, object_name, subresource=None, expiration=expiration, http_method='GET',
                                      query_parameters=None, headers=None)

            return make_response(jsonify({"status": API_SUCCESS_STATUS, "url": url}), 200)
        except Exception as e:
            error = APIError(error_code='', error_message=str(e), traceback=traceback.format_exc())
            return make_response(jsonify({'message': 'failure!!', 'error': error.make_error_response()}))


class GcsObjectUrl(Resource):
    def post(self):
        bucket_name = request.json.get('bucket_name', 'test-bucket0425')
        object_name = request.json.get('object_name', 'add_item (1).xlsx')
        expiration = request.json.get('expiration', 120)
        try:
            signed_urls = []
            gcp_storage_client = storage.Client()
            bucket = gcp_storage_client.get_bucket(bucket_name)
            signed_url = bucket.blob(object_name).generate_signed_url(expiration=expiration)
            app.logger.debug(signed_url)
            signed_urls.append({'url': signed_url})

            return make_response(jsonify({'status': API_SUCCESS_STATUS, "message": signed_urls}), 200)

        except Exception as e:
            app.logger.debug(e)
            error = APIError(error_code='', error_message=str(e), traceback=traceback.format_exc())
            return make_response(jsonify({'status': API_ERROR_STATUS, 'errors': error.make_error_response()}), 500)


api.add_resource(GcsObjectUrl, '/gcsobjecturl')
api.add_resource(CustomObjectSignedUrl, '/customsignedgcsobjecturl')