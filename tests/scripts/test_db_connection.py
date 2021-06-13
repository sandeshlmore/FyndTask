from bson import ObjectId
from pymongo import MongoClient

from common.constants import MONGO_URI, DB_NAME

mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]


result = db.testing.delete_one({'_id': ObjectId('60c4445623f90b2f54bcbd6d')})
print(result.raw_result)
doc = {
    "_id" : ObjectId("60c4445623f90b2f54bcbd6d"),
    "99popularity" : 83.0,
    "director" : "Victor Fleming",
    "genre" : [
        "Adventure",
        " Family",
        " Fantasy",
        " Musical"
    ],
    "imdb_score" : 8.3,
    "name" : "The Wizard of Oz",
    "key":2
}
res = db.testing.insert_one(doc)
print(res.inserted_id)