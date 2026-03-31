def filter_no_traceback(record) -> bool:
    setattr(record, "exc_info", None)
    return True
