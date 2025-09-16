# app/blueprints/api/routes.py
from . import api_bp
from flask import (
    app,
    json,
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
from app.utils.merge_q_generator import merge_q_generator
from app.utils.data_retriever import *
from app.extensions import db, get_redis
from app.models import UserRole, MergeHistory
import json as py_json
import hashlib
from sqlalchemy import text


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
# @api_bp.route("/user/schemas", methods=["GET"])
# @login_required
# def user_schemas():
#     schemas = get_schemas_for_user(current_user.user_id)
#     print(schemas)
#     return jsonify({"available_schemas": schemas}), 200


# Data Retrieval
@api_bp.route("/data/get/table_options", methods=["GET"])
@login_required
def table_options():
    options = get_table_options(current_user.user_id)
    return jsonify({"table_select_options": options}), 200

@api_bp.route("/data/get/tracker_options", methods=["GET"])
@login_required
def tracker_options():
    options = get_tracker_options(current_user.user_id)
    return jsonify({"tracker_select_options": options}), 200

@api_bp.route("/data/action/merge", methods=["POST"])
@login_required
def merge_data():
    data = request.json
    # Logic to merge data
    merged_key, sql_query = merge_q_generator(data)
    # return jsonify(sql_query), 200
    redis_key = f"merged_data:{merged_key}"
    redis_client = get_redis()
    if not redis_client.exists(redis_key): #if not in cache, query and store
        result = db.session.execute(text(sql_query))
        merged_data = [dict(row._mapping) for row in result.fetchall()]
        redis_client.setex(redis_key, 3600, py_json.dumps(merged_data))
    else:
        merged_data = py_json.loads(redis_client.get(redis_key))

    history = MergeHistory(
        user_id=current_user.user_id,
        merged_key=merged_key,
        selected_tables=json.dumps(data),
    )
    db.session.add(history)
    db.session.commit()
    return jsonify({"message": "Merge successful", "redis_key": redis_key}), 200

@api_bp.route("/data/action/download/<key>", methods=["GET"])
@login_required
def download_merged_data(key):
    redis_client = get_redis()
    merged_data = redis_client.get(key)
    if not merged_data:
        return jsonify({"error": "No merged data found"}), 404
    return jsonify({"data": py_json.loads(merged_data)}), 200
