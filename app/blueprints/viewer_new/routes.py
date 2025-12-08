# blueprints/viewer/routes.py
from . import viewer_bp_new
from flask import render_template, request, url_for, current_app as app
from flask_login import current_user
from app.extensions import get_redis
import json


@viewer_bp_new.route("/")
def data_viewer_new():
    # If the user is logged out, force a refresh
    if not current_user.is_authenticated:
        return render_template("data_viewer_new.html", link_url=app.config.get("DATA_VIEWER_DOCS_URL", "#"))
    # If the request is a normal navigation (not a reload), check referrer
    if request.referrer and request.referrer.endswith(url_for(".data_viewer_new")) and request.headers.get("Cache-Control") != "max-age=0":
        return "", 204  # No Content, do not re-render
    return render_template("data_viewer_new.html", link_url=app.config.get("DATA_VIEWER_DOCS_URL", "#"))

@viewer_bp_new.route("/result/<key>")
def data_viewer_result(key):
    redis_client = get_redis()
    data = redis_client.get(key).decode("utf-8")
    data = json.loads(data)
    return render_template("data_viewer_popup.html", results=data)
