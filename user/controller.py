import datetime

from master.views import db


def user_login(email):
    user_info = db.users.find_one({'email': email}, {"_id": 0})
    return user_info


def blacklist_token(jti):
    db.blacklisted_tokens.update({'jti': jti}, {'$set': {'jti': jti, 'datetime': datetime.datetime.utcnow()}},
                                           upsert=True)

