import json

from pymongo import MongoClient
import os

from common.constants import MONGO_URI, DB_NAME

mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]

f = open('./imdb.json t.json')

movies = json.load(f)

db.movies.remove()
db.movies.insert_many(movies)