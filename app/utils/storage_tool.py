from flask import current_app


def get_redis():
    return current_app.extensions.get("redis", None)
