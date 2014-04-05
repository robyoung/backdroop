import json

from flask import Flask

from .models import FilesystemDataSets


app = Flask("backdrop.webapp")

datasets = FilesystemDataSets()


@app.route("/_status", methods=["GET"])
def status():
    return "ok"


@app.route("/data-sets", methods=["GET"])
def list_data_sets():
    return jsonify(datasets.list())


@app.route("/data-sets/<data_set_id>", methods=["POST"])
def post_to_data_set(data_set_id):
    return "post"


@app.route("/data-sets/<data_set_id>", methods=["GET"])
def query_data_set(data_set_id):
    return "query"

# Helper functions
def jsonify(data):
    return app.response_class(json.dumps(data, indent=2))
