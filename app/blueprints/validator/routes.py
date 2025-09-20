# app/blueprints/validator/routes.py
from . import validator_bp
from app.extensions import db, get_redis
from app.models import TrackerForm
from flask import render_template, request, session as flask_session, jsonify, url_for
from flask_login import current_user

@validator_bp.route("/")
def validate():
    # If the user is logged out, force a refresh
    if not current_user.is_authenticated:
        return render_template("test_validator.html", title="Test Validator")
    
    # If the request is a normal navigation (not a reload), check referrer
    if request.referrer and request.referrer.endswith(url_for(".validate")) and request.headers.get("Cache-Control") != "max-age=0":
        return "", 204  # No Content, do not re-render
    return render_template("test_validator.html", title="Test Validator")
