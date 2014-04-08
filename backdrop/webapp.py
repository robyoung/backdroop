import json
from functools import partial

from flask import Flask, request
from jsonschema import validate, FormatChecker
from bson import ObjectId
import datetime

from .models import FilesystemDataSets, NotFound
from .storage.mongo import MongoData
from .data import parse_values, add_meta_fields
from .query import validate_query, parse_query_args, validate_query_args


app = Flask("backdrop.webapp")

datasets = FilesystemDataSets()
datasets_data = MongoData('localhost', 'backdroop')


@app.route("/_status", methods=["GET"])
def status():
    return "ok"


@app.route("/data-sets", methods=["GET"])
def list_data_sets():
    return jsonify(datasets.list())


@app.route("/data-sets/<data_set_id>", methods=["GET"])
def get_a_data_set(data_set_id):
    try:
        return jsonify(datasets.get(data_set_id))
    except NotFound:
        return jsonify({"error": "Not found"}), 404


@app.route("/data-sets/<data_set_id>/data", methods=["POST"])
def post_to_data_set(data_set_id):
    try:
        data_set = datasets.get(data_set_id)

        # Create the data set if it doesn't exist
        if not datasets_data.exists(data_set_id):
            datasets_data.create(
                    data_set_id,
                    data_set.get("capped", False),
                    data_set.get("cap_size", 0),
                    data_set.get("schema", {}))

        
        # Save the records
        records = listify(request.json)
        # Validate each record, currently would raise an exception
        validate_ = partial(validate,
                            schema=data_set['schema'],
                            format_checker=FormatChecker())
        map(validate_, records)
        # Parse formatted strings (ie. date times)
        records = map(partial(parse_values,
                              schema=data_set['schema']), records)
        # Add meta fields ie. period start fields
        records = map(add_meta_fields, records)

        datasets_data.save(data_set_id, records)
        
        return jsonify({"status": "ok", "saved": len(records)})
    except NotFound:
        return jsonify({"error":"Not found"}), 404


@app.route("/data-sets/<data_set_id>/data", methods=["GET"])
def query_data_set(data_set_id):
    try:
        data_set = datasets.get(data_set_id)
        
        validate_query_args(request.args)
        query = parse_query_args(request.args)

        validate_query(query, data_set["schema"])

        results = datasets_data.query(data_set_id, query)

        return jsonify(results)
    except NotFound:
        return jsonify({"error": "Not found"}), 404

# Helper functions
class JsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

def jsonify(data):
    return app.response_class(json.dumps(data, indent=2, cls=JsonEncoder))

def listify(data):
    """Wrap value in a list if it is not already a list
    >>> listify("foo")
    ['foo']
    >>> listify(["foo"])
    ['foo']
    """
    return data if isinstance(data, list) else [data]
