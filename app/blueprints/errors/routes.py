# app/blueprints/errors/routes.py
from . import errors_bp
from flask import request, jsonify

@errors_bp.app_errorhandler(404)
def not_found(error):
    # If the request wants JSON (API clients), return JSON
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        return jsonify({"error": "Not found", "status": 404}), 404
    # For browser navigation (non-API), return JSON anyway so React handles it
    return jsonify({"error": "Not found", "status": 404}), 404

@errors_bp.app_errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "status": 500}), 500

@errors_bp.app_errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "status": 400}), 400