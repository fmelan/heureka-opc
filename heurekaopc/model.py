from contextlib import contextmanager

import pymongo

from settings import settings


@contextmanager
def mongo_client(*args, **kwds):
    dbclient = pymongo.MongoClient(settings.mongodb_connstring)
    db = dbclient[settings.database_name]
    try:
        yield db
    finally:
        dbclient.close()
