# app/blueprints/tracker/routes.py
from flask import render_template, request, session as flask_session, jsonify, url_for

# from app.extensions import google, s3, s3_bucket
from app.utils.emailer import send_email
from app.utils.option_loader import load_form_options
from app.models import TrackerForm
from app.extensions import db, get_email_list
from . import tracker_bp


@tracker_bp.route("/")
def test_tracker():
    # If the user is logged out, force a refresh
    if not flask_session.get("logged_in"):
        return render_template("test_tracker.html", title="Test Tracker")

    # If the request is a normal navigation (not a reload), check referrer
    if request.referrer and request.referrer.endswith(url_for(".test_tracker")) and request.headers.get("Cache-Control") != "max-age=0":
        return "", 204  # No Content, do not re-render
    return render_template("test_tracker.html", title="Test Tracker")
