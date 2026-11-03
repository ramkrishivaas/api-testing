def multipart_fields(fields):
    """Convert regular fields to Requests multipart form fields."""
    return [
        (key, (None, "" if value is None else str(value)))
        for key, value in fields.items()
    ]