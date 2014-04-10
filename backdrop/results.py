import re

def strip_period_starts(result):
    return dict((field, value) for field, value in result.items() if not is_period_start(field))

def is_period_start(field):
    return re.search('^_.*_start_at$', field)

def add_period_limits(query, result):
    period = query.get('period')
    if period:
        start_at = result[period.start_at_key]
        end_at = period.end(start_at)
        return dict(result.items() + [('_start_at', start_at), ('_end_at', end_at)])
    return result
