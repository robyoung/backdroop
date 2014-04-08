
def strip_internal_fields(result):
    return dict((field, value) for field, value in result.items() if not is_period_start(field))

def is_period_start(field):
    return field.startswith("_") and field.endswith("_start_at")
