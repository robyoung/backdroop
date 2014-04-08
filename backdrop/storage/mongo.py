from pymongo import Connection
import pymongo
from bson import Code

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
        if is_group_query(query):
            return self._group_query(data_set_id, query)
        else:
            return self._raw_query(data_set_id, query)

    def _group_query(self, data_set_id, query):
        keys = get_group_keys(query)
        spec = get_mongo_spec(query)
        collect_fields = get_unique_collect_fields(query)

        return self._db[data_set_id].group(
            keys = keys,
            condition = build_group_condition(keys, spec),
            initial = build_group_initial_state(collect_fields),
            reduce = Code(build_group_reducer(collect_fields)))


    def _raw_query(self, data_set_id, query):
        spec = get_mongo_spec(query)
        sort = get_mongo_sort(query)
        limit = get_mongo_limit(query)

        return self._db[data_set_id].find(spec, sort=sort, limit=limit)


def is_group_query(query):
    return query.get("group_by") or query.get("period")


def get_mongo_limit(query):
    """
    >>> get_mongo_limit({})
    0
    >>> get_mongo_limit({"limit": 100})
    100
    """
    return query.get("limit", 0)


# TODO: make sort spec less shit
def get_mongo_sort(query):
    """
    >>> get_mongo_sort({})
    >>> get_mongo_sort({"sort_by": {"field": "foo", "direction": "ascending"}})
    [('foo', 1)]
    """
    if query.get("sort_by"):
        direction = get_mongo_sort_direction(query["sort_by"]["direction"])
        return [(query["sort_by"]["field"], direction)]

def get_mongo_sort_direction(direction):
    """
    >>> get_mongo_sort_direction("invalid")
    >>> get_mongo_sort_direction("ascending")
    1
    >>> get_mongo_sort_direction("descending")
    -1
    """
    return {
        "ascending": pymongo.ASCENDING,
        "descending": pymongo.DESCENDING,
    }.get(direction)

def get_mongo_spec(query):
    filter_by = query.get("filter_by", {})
    time_range = time_range_to_mongo_query(query.get("start_at"), query.get("end_at"))

    return dict(filter_by.items() + time_range.items())


def time_range_to_mongo_query(start_at, end_at):
    """
    >>> from datetime import datetime as dt
    >>> time_range_to_mongo_query(dt(2012, 12, 12, 12), None)
    {'_timestamp': {'$gte': datetime.datetime(2012, 12, 12, 12, 0)}}
    >>> time_range_to_mongo_query(dt(2012, 12, 12, 12), dt(2012, 12, 13, 13))
    {'_timestamp': {'$gte': datetime.datetime(2012, 12, 12, 12, 0), '$lt': datetime.datetime(2012, 12, 13, 13, 0)}}
    >>> time_range_to_mongo_query(None, None)
    {}
    """
    mongo = {}
    if start_at or end_at:
        mongo['_timestamp'] = {}

        if start_at:
            mongo['_timestamp']['$gte'] = start_at
        if end_at:
            mongo['_timestamp']['$lt'] = end_at

    return mongo


def get_unique_collect_fields(query):
    """
    >>> get_unique_collect_fields({"collect":[["foo", "sum"]]})
    ['foo']
    """
    return list(set([field for field, _ in query.get("collect", [])]))


def get_group_keys(query):
    """
    >>> from backdrop.timeutils import WEEK
    >>> get_group_keys({"group_by": "foo"})
    ['foo']
    >>> get_group_keys({"period": WEEK})
    ['_week_start_at']
    >>> get_group_keys({"group_by": "foo", "period": WEEK})
    ['foo', '_week_start_at']
    """
    keys = []
    if query.get("group_by"):
        keys.append(query["group_by"])
    if query.get("period"):
        keys.append(query["period"].start_at_key)
    return keys


def build_group_condition(keys, spec):
    """
    >>> build_group_condition(["foo"], {"bar": "doo"})
    {'foo': {'$ne': None}, 'bar': 'doo'}
    >>> build_group_condition(["foo"], {"foo": "bar"})
    {'foo': 'bar'}
    """
    key_filter = [(key, {'$ne':None}) for key in keys if key not in spec]
    return dict(spec.items() + key_filter)


def build_group_initial_state(collect_fields):
    """
    >>> build_group_initial_state([])
    {'_count': 0}
    >>> build_group_initial_state(["foo"])
    {'_count': 0, 'foo': []}
    """
    initial = {'_count': 0}
    for field in  collect_fields:
        initial[field] = []
    return initial


def build_group_reducer(collect_fields):
    template = "function (current, previous)" \
               "{{ previous._count++; {collectors} }}"
    return template.format(
            collectors=map(_build_collector_code, collect_fields))

def _build_collector_code(collect_field):
    template = "if (current['{c}'] !== undefined) " \
               "{{ previous['{c}'].push(current['{c}']); }}"
    return template.format(c=clean_collect_field(collect_field))

def clean_collect_field(collect_field):
    """
    WTF python escaping!?
    >>> clean_collect_field('foo\\\\bar')
    'foo\\\\\\\\bar'
    >>> clean_collect_field("foo'bar")
    "foo\\\\\'bar"
    """
    return collect_field.replace('\\', '\\\\').replace("'", "\\'")
