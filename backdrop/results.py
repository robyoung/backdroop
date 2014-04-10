import re
from functools import partial


__all__ = ['build_results']


def create_result_builder(query):
    """Return a function that builds result items

    - Add period limits to period queries
    - Strip meta fields for period start
    """
    funcs = [
        partial(add_period_limits, query),
        strip_period_starts
    ]
    def result_builder(result):
        return reduce(lambda result, func: func(result), [result] + funcs)
    return result_builder


def strip_period_starts(result):
    return dict((field, value) for field, value in result.items() if not is_period_start(field))


def is_period_start(field):
    """
    >>> is_period_start("_start_at")
    False
    >>> is_period_start("_week_start_at")
    True
    """
    return bool(re.search('^_.*_start_at$', field))


def add_period_limits(query, result):
    period = query.get('period')
    if period:
        start_at = result[period.start_at_key]
        end_at = period.end(start_at)
        return dict(result.items() + [('_start_at', start_at), ('_end_at', end_at)])
    return result
