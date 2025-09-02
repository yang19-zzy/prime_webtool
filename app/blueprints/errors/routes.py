# app/blueprints/errors/routes.py
from . import errors_bp
from flask import (
    app,
    request,
    redirect,
    url_for,
    session as flask_session,
    make_response,
    jsonify,
    render_template,
    current_app,
)

@errors_bp.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

@errors_bp.app_errorhandler(400)
def bad_request(error):
    return render_template("400.html"), 400
