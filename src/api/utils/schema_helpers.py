try:
    from drf_spectacular.utils import extend_schema, inline_serializer
except ImportError:

    def extend_schema(*args, **kwargs):  # type: ignore
        def decorator(f):
            return f

        return decorator

    def inline_serializer(*args, **kwargs):  # type: ignore
        pass
