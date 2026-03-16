from datetime import datetime


def to_date(value):
    if isinstance(value, datetime):
        return value.date()
    return value
