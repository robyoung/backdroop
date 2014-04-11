"""
This module handles validtion and processing of incoming records
"""
from functools import partial

from dateutil.parser import parse as parse_datetime
from jsonschema import validate, FormatChecker

from .timeutils import PERIODS


__all__ = ['create_record_parser']


def create_record_parser(schema):
    """Return a function that parses incoming records and adds meta fields

    - Validate records against the JSONSchema
    - Parse datetime fields based on the JSONSchema
    - Add meta fields for period start tiestamps
    """
    def record_parser(record):
        validate_record(record, schema)
        
        record = parse_values(record, schema)
        record = add_meta_fields(record)

        return record

    return record_parser


def validate_record(record, schema):
    validate(record, schema=schema, format_checker=FormatChecker())


def parse_values(record, schema):
    """Parse values that cannot be represented in JSON
    >>> fields = {"field": {"type": "string", "format": "date-time"}}
    >>> schema = {"properties": fields}
    >>> record = {"field": "2012-12-12T00:00:00+00:00"}
    >>> parse_values(record, schema)
    {'field': datetime.datetime(2012, 12, 12, 0, 0, tzinfo=tzutc())}
    """
    for field_name, field in schema['properties'].items():
        if field.get('format') == "date-time":
            if field_name in record:
                record[field_name] = parse_datetime(record[field_name])

    return record


def add_meta_fields(record):
    """
    >>> from datetime import datetime
    >>> add_meta_fields({'_timestamp': datetime(2012, 12, 12)}).keys()
    ['_timestamp', '_hour_start_at', '_day_start_at', '_month_start_at', '_week_start_at', '_quarter_start_at']
    """
    if "_timestamp" in record:
        for period in PERIODS:
            period_start = period.start(record['_timestamp'])

            record = add_fields(record, **{
                period.start_at_key:period_start})
    return record


def add_fields(record, **kwargs):
    """
    >>> add_fields({}, foo="bar")
    {'foo': 'bar'}
    >>> add_fields({"foo":"foo"}, foo="bar")
    {'foo': 'bar'}
    """
    return dict(record.items() + kwargs.items())
