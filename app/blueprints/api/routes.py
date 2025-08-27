# app/blueprints/api/routes.py
from . import api_bp
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
from flask_login import current_user, login_required
from app.utils.data_retriever import *
from app.extensions import db


# User Management - user profile view, update/edit
@api_bp.route("/user/profile", methods=["GET"])
@login_required
def user_profile():
    user_profile = get_profile_for_user(current_user.user_id)
    return jsonify({"user_profile": user_profile}), 200

@api_bp.route("/admin/users", methods=["GET"])
@login_required
def list_users():
    users = get_all_users()
    return jsonify({"users": users}), 200

@api_bp.route("/admin/user/<user_id>/inlab", methods=["POST"])
@login_required
def set_user_in_lab(user_id):
    # Logic to set user as in-lab or not
    user = UserRole.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.in_lab_user = not user.in_lab_user
    db.session.commit()
    return jsonify({"message": "User in-lab status updated"}), 200

# Data Access Management
@api_bp.route("/user/schemas/<user_id>", methods=["GET"])
@login_required
def user_schemas(user_id):
    schemas = get_schemas_for_user(user_id)
    print(schemas)
    return jsonify({"available_schemas": schemas}), 200


# Data Retrieval
