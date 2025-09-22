# app/blueprints/tracker/routes.py
from . import tracker_bp

from flask import render_template, request, url_for
from flask_login import current_user

@tracker_bp.route("/")
def test_tracker():
    # If the user is logged out, force a refresh
    if not current_user.is_authenticated:
        return render_template("test_tracker.html", title="Test Tracker")

    # If the request is a normal navigation (not a reload), check referrer
    if request.referrer and request.referrer.endswith(url_for(".test_tracker")) and request.headers.get("Cache-Control") != "max-age=0":
        return "", 204  # No Content, do not re-render
    return render_template("test_tracker.html", title="Test Tracker")
