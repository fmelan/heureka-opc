import pymongo

from settings import settings

dbclient = pymongo.MongoClient(settings.mongodb_connstring)
db = dbclient[settings.database_name]
