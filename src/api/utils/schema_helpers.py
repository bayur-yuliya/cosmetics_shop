try:
    from drf_spectacular.utils import extend_schema, inline_serializer
except ImportError:

    def extend_schema(*args, **kwargs):
        def decorator(f):
            return f

        return decorator

    def inline_serializer(*args, **kwargs):
        pass
