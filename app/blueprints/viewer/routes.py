# blueprints/viewer/routes.py
from . import viewer_bp
from flask import render_template, request, url_for, current_app as app
from flask_login import current_user


@viewer_bp.route("/")
def data_viewer():
    # If the user is logged out, force a refresh
    if not current_user.is_authenticated:
        return render_template("data_viewer.html", link_url=app.config.get("DATA_VIEWER_DOCS_URL", "#"))
    # If the request is a normal navigation (not a reload), check referrer
    if request.referrer and request.referrer.endswith(url_for(".data_viewer")) and request.headers.get("Cache-Control") != "max-age=0":
        return "", 204  # No Content, do not re-render
    return render_template("data_viewer.html", link_url=app.config.get("DATA_VIEWER_DOCS_URL", "#"))