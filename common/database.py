import pymongo
import os

class Database(object):
    Uri = "mongodb://127.0.0.1:27017"
    online = "mongodb://ithollie:hawaibrahB1a@ds023478.mlab.com:23478/full_stack"
    DATABASE = None

    def __init(self):
        pass

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.connectUrl(Database.Uri, Database.online))
        Database.DATABASE = client['full_stack']

    @staticmethod
    def connectUrl(uri_connection, online_connection):
        if online_connection is not None:
            return online_connection

    @staticmethod
    def collectionexists(collection):
        if Database.DATABASE[collection]:
            return True
        else:
            return False

    @staticmethod
    def dropCollection(collection):
        Database.DATABASE[collection].drop()


    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)


    @staticmethod
    def updates(collection, data, data1):
        Database.DATABASE[collection].update(data, data1)

    @staticmethod
    def delete(collection, data):
        Database.DATABASE[collection].remove(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)
