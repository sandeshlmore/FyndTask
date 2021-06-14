import datetime

import bcrypt
from flask import request, make_response, jsonify, Blueprint
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt_claims, \
    jwt_refresh_token_required, get_jti
from flask_restful import Resource

from common.constants import JWT_REFRESH_TOKEN_TIMEDELTA, JWT_ACCESS_TOKEN_TIMEDELTA, API_SUCCESS_STATUS, \
    API_ERROR_STATUS
from master.views import api, db, app
from user.controller import user_login, blacklist_token

user_blueprint = Blueprint('user_blueprint', __name__)

class User(object):

    def __init__(self, user_email, user_name, user_password, is_admin):
        self.email = user_email
        self.user_name = user_name
        self.user_password = user_password
        self.is_admin = is_admin


class Login(Resource):
    '''
        #Provides accessToken(for 15min) and RefreshToken(24 mins) for using protected Apis
        email: user email id
        password: user password

    '''
    def post(self):
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        user = user_login(email)
        if not user:
            return make_response(
                jsonify({'status': API_SUCCESS_STATUS, 'message': "user with email '{}' doesn't exist.".format(email)}), 200)

        password = password.encode()
        checkpw = bcrypt.checkpw(password, user.get('password'))

        if not checkpw:
            return make_response(jsonify({'status': API_SUCCESS_STATUS, 'message': "INVALID_USER_PASSWORD"}), 200)

        user_claims = {'is_admin': user.get('is_admin')}
        access_token = create_access_token(identity=user.get('email'), user_claims=user_claims,
                                           expires_delta=JWT_ACCESS_TOKEN_TIMEDELTA)
        refresh_token = create_refresh_token(identity=user.get('email'),
                                             user_claims=user_claims,
                                             expires_delta=JWT_REFRESH_TOKEN_TIMEDELTA)

        # blacklist old access_token refresh_token tokens
        old_access_token = user.get('access_token', '')
        old_refresh_token = user.get('refresh_token', '')
        try:
            old_access_token_jti = get_jti(old_access_token)
            old_refresh_token_jti = get_jti(old_refresh_token)
            if old_access_token:
                blacklist_token(old_access_token_jti)
                app.logger.debug('old_access_token blacklisted')
            if old_refresh_token:
                blacklist_token(old_refresh_token_jti)
                app.logger.debug('old_refresh_token blacklisted')
        except Exception as e:
            app.logger.debug(e)

        db.users.update({'email': email}, {'$set': {'access_token': access_token, 'refresh_token': refresh_token,
                                                    'last_logged_in': datetime.datetime.now()}})

        return make_response(jsonify({'status': API_SUCCESS_STATUS, 'message': "LOGIN_SUCCESSFULLY",
                                      'access_token': access_token, 'refresh_token': refresh_token}), 200)


class TokenRefresh(Resource):
    '''
        #Gernerate new access token using existing refresh token
    '''
    @jwt_refresh_token_required
    def post(self):
        try:
            current_user = get_jwt_identity()
            user_claims = get_jwt_claims()
            app.logger.debug('user_claims')
            app.logger.debug(user_claims)
            access_token = create_access_token(identity=current_user, user_claims=user_claims
                                               , expires_delta=JWT_ACCESS_TOKEN_TIMEDELTA)
            return make_response(jsonify({'status': API_SUCCESS_STATUS, 'message': 'Access Token Generated',
                                          'access_token': access_token}), 200)
        except Exception as e:
            app.logger.error(e)
            return make_response(jsonify({'status': API_ERROR_STATUS, 'message': 'Something went wrong'}), 500)
        
        
class HealthCheck(Resource):

    def get(self):
        return make_response(jsonify({'status': 'OK'}), 200)


api.add_resource(HealthCheck, '/health-check')
api.add_resource(Login, '/user/login')
api.add_resource(TokenRefresh, '/refresh-token')
