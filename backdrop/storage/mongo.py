from pymongo import Connection

from .base import Data


__all__ = ["MongoData"]


def collection_name_from_id(data_set_id):
    """Calculate the Mongo collection name from the data set id"""
    return data_set_id

class MongoData(Data):
    def __init__(self, host, database):
        self._mongo = Connection(host)
        self._db = self._mongo[database]

    def exists(self, data_set_id):
        collection_name = collection_name_from_id(data_set_id)
        return collection_name in self._db.collection_names()

    def create(self, data_set_id, capped, size, schema):
        # Create collection
        if capped:
            self._db.create_collection(data_set_id, capped=capped, size=size)
        else:
            self._db.create_collection(data_set_id)

        # Create indexes for fields that are defined and required
        # TODO: Figure out how to calculate meta fields that need indexing, ie. period start fields
        required = schema.get("required", [])
        for field_name, field_meta in schema.get("properties", {}).items():
            if field_name in required:
                self._db[data_set_id].create_index(field_name)

    def save(self, data_set_id, records):
        for record in records:
            self._db[data_set_id].save(record)

    def query(self, data_set_id, query):
        pass
