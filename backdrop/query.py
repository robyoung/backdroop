import jsonschema

class ValidationError(StandardError):
    pass

query_schema2 = {
    "properties": {
        "start_at": {
            "type": "array",
            "maxItems": 1,
            "items": {"type": "string", "format": "date-time"}
        },
        "end_at": {
            "type": "array",
            "maxItems": 1,
            "items": {"type": "string", "format": "date-time"}
        },
        "filter_by": {
            "type": "array",
            "items": {"type": "string", "pattern": "^[a-z0-9_]+:.*$"},
            "uniqueItems": True
        },
        "period": {
            "type": "array",
            "maxItems": 1,
            "items": {"enum": ["hour", "day", "week", "month", "quarter"]}
        },
        "group_by": {
            "type": "array",
            "maxItems": 1,
            "items": {"type": "string", "pattern": "^[a-z0-9_]+$"}
        },
        "sort_by": {
            "type": "array",
            "maxItems": 1,
            "items": {"type": "string", "pattern": "^[a-z0-9_]+:(ascending|descending)$"}
        },
        "limit": {
            "type": "array",
            "maxItems": 1,
            "items": {"type": "string", "pattern": "^[0-9]+$"}
        },
        "collect": {
            "type": "array",
            "items": {"type": "string", "pattern": "^[a-z0-9_]+:(sum|count|set|mean)$"},
            "uniqueItems": True
        }
    },
    "additionalProperties": False
}

query_schema = {
    "title": "Query",
    "properties": {
        "start_at": {
            "type": "string",
            "format": "date-time"
        },
        "end_at": {
            "type": "string",
            "format": "date-time"
        },
        "filter_by": {
            "type": "object",
            "$ref": "#/definitions/filter_by"
        },
        "period": {
            "enum": ["hour", "day", "week", "month", "quarter"]
        },
        "group_by": {
            "type": "string",
        },
        "sort_by": {
            "type": "object",
            "$ref": "#/definitions/sort_by"
        },
        "limit": {
            "type": "integer",
            "minimum": 0
        },
        "collect": {
            "type": "object",
            "$ref": "#/definitions/collect"
        }
    },
    "additionalProperties": False,
    "definitions": {
        "filter_by": {
            "patternProperties": {
                "^[a-z0-9_]+$": {
                    "type": "string"
                }
            },
            "additionalProperties": False
        },
        "sort_by": {
            "properties": {
                "field": { "type": "string" },
                "direction": { "enum": ["ascending", "descending"] }
            },
            "required": ["field", "direction"],
            "additionalProperties": False
        },
        "collect": {
            "patternProperties": {
                "^[a-z0-9_]+$": {
                    "enum": ["sum", "count", "set", "mean"]
                }
            },
            "additionalProperties": False
        }
    }
}

def validate_query_args(args):
    query_args = dict((key, args.getlist(key)) for key in args.keys())
    jsonschema.validate(query_args, query_schema2)

def parse_query_args(args):
    query = {}

    if "start_at" in args:
        query['start_at'] = args.get('start_at')
    if "end_at" in args:
        query['end_at'] = args.get('end_at')
    if "filter_by" in args:
        query["filter_by"] = {}
        for filter_by in args.getlist("filter_by"):
            field, value = filter_by.split(":", 1)
            query["filter_by"][field] = value
    if "period" in args:
        query["period"] = args.get("period")
    if "group_by" in args:
        query["group_by"] = args.get("group_by")
    if "sort_by" in args:
        field, direction = args.get("sort_by").split(":", 1)
        query["sort_by"] = {"field": field, "direction": direction}
    if "limit" in args:
        query["limit"] = args.get("limit", type=int)
    if "collect" in args:
        query["collect"] = {}
        for collect in args.getlist("collect"):
            field, function = collect.split(":", 1)
            query["collect"][field] = function
    
    return query

def validate_query(query, schema):
    # validate that the query is correct
    jsonschema.validate(query, query_schema)
    # validate that the query is valid with respect to the provided schema
    
    # start_at, end_at and period are only valid if the schema has _timestamp
    if "_timestamp" not in schema['properties']:
        for field in ["start_at", "end_at", "period"]:
            if field in query:
                raise
    
    # can filter on any core field
    for field, value in query.get("filter_by", {}).items():
        if field not in schema["properties"]:
            raise

    # can group on any core fields
    if "group_by" in query and query["group_by"] not in schema["properties"]:
        raise ValidationError("Cannot group by {}, field not present".format(query["group_by"]))

    # can sort by any core field
    if "sort_by" in query and query["sort_by"]["field"] not in schema["properties"]:
        raise ValidationError("Cannot sort by {}, field not present".format(query["sort_by"]["field"]))

    # can collect any core field
    for field, function in query.get("collect", {}).items():
        if field not in schema["properties"]:
            raise ValidationError("Cannot collect on {}, field not present".format(field))
