from dateutil.parser import parse as parse_datetime

from .timeseries import PERIODS

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
    if "_timestamp" in record:
        for period in PERIODS:
            record[period.start_at_key] = period.start(
                    record['_timestamp'])
    return record
