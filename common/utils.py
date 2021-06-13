from functools import wraps
from json import JSONEncoder

from bson import ObjectId, json_util
from flask import jsonify, make_response
from flask_jwt_extended import JWTManager, get_jwt_identity, get_jwt_claims

from common.constants import API_SUCCESS_STATUS

jwt = JWTManager()


class MongoJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json_util.default(obj, json_util.CANONICAL_JSON_OPTIONS)


def check_admin_access(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        user_claims = get_jwt_claims()
        # print('current_user')
        # print(current_user)
        # print('user_claims')
        # print(user_claims)
        ##TODO: when the user access level is changed need to blacklist the tokens of the user
        if user_claims.get('is_admin'):
            return fn(*args, **kwargs)
        else:
            return make_response(jsonify({'status': API_SUCCESS_STATUS, 'message': 'USER_ACCESS_RESTRICTED'}), 200)

    return wrapper