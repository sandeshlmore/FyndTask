from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from pymongo import MongoClient

from common.constants import MONGO_URI, DB_NAME, APP_SECRET_KEY
from common.utils import MongoJsonEncoder, jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY
app.json_encoder = MongoJsonEncoder
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['PROPAGATE_EXCEPTIONS'] = True  ##TODO: check issue with exception propagation
CORS(app, resources={r"*": {"origins": "*"}})

jwt.init_app(app)

api = Api(app)
# jwt._set_error_handler_callbacks(api)

mongo = MongoClient(MONGO_URI, connect=False)
db = mongo[DB_NAME]


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    val = is_jti_blacklisted(jti)
    return val


def is_jti_blacklisted(jti):
    try:
        response = mongo.db.blacklisted_tokens.find_one({'jti': jti})
        return bool(response)
    except Exception as e:
        app.logger.error(str(e))
        return False


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True, threaded=True)
