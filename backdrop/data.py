from dateutil.parser import parse as parse_datetime

from .timeutils import PERIODS

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
