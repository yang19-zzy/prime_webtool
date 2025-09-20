# app/blueprints/api/routes.py
from . import api_bp
from flask import (
    request,
    session as flask_session,
    jsonify
)
from flask_login import current_user, login_required
from app.extensions import db, get_redis, get_email_list
from app.models import UserRole, MergeHistory
from app.utils.data_retriever import *
from app.utils.merge_q_generator import merge_q_generator
from app.utils.emailer import send_email
from sqlalchemy import text

import base64
from datetime import date, datetime
from decimal import Decimal
import json
import uuid


def _json_serializer(obj):
    """Serialize non-JSON-native types coming from the DB into JSON-friendly values."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        # choose float or str depending on precision needs
        return float(obj)
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode("ascii")
    raise TypeError(f"Type {type(obj)} not serializable")


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


@api_bp.route("/data/get/unvalidated_forms", methods=["GET"])
@login_required
def unvalidated_forms():
    forms = get_unvalidated_forms(current_user.user_id)
    return jsonify({"unvalidated_forms": forms}), 200


@api_bp.route("/data/action/merge", methods=["POST"])
@login_required
def merge_data():
    data = request.json
    # Logic to merge data
    merged_key, sql_query = merge_q_generator(data)
    redis_key = f"merged_data:{merged_key}"
    redis_client = get_redis()

    if not redis_client.exists(redis_key):  # if not in cache, query and store
        result = db.session.execute(text(sql_query))
        merged_data = [dict(row._mapping) for row in result.fetchall()]

        # Serialize with custom handler to convert datetimes, Decimals, UUIDs, etc.
        serialized = json.dumps(merged_data, default=_json_serializer, sort_keys=False)
        # Store the serialized JSON string in Redis with TTL (setex expects bytes/str)
        redis_client.setex(redis_key, 3600, serialized)
    else:
        raw = redis_client.get(redis_key)
        # redis returns bytes, decode before json.loads
        if raw is None:
            merged_data = []
        else:
            merged_data = json.loads(raw.decode("utf-8"))

    history = MergeHistory(
        user_id=current_user.user_id,
        merged_key=merged_key,
        selected_tables=json.dumps(data),
    )
    db.session.add(history)
    db.session.commit()
    return jsonify({"message": "Merge successful", "redis_key": redis_key, 'query': sql_query}), 200

# @api_bp.route("/data/action/download/<key>", methods=["GET"])
# @login_required
# def download_merged_data(key):
#     redis_client = get_redis()
#     merged_data = redis_client.get(key)
#     if not merged_data:
#         return jsonify({"error": "No merged data found"}), 404
#     return jsonify({"data": py_json.loads(merged_data)}), 200

@api_bp.route("/data/action/submit_tracker_form", methods=["POST"])
@login_required
def submit_tracker_form():
    form_data = request.json
    metadata = form_data.get("metadata", {})
    # devices = form_data.get("devices", [])
    # form_owner = metadata.get("form_owner") or current_user.user_id
    subject_id = metadata.get("subject_id")

    send_email(
        recipient=get_email_list(),
        subject="⚠️ New Form Submitted [PRIME Lab In-lab Tracker]",
        message_text=f"PRIME Lab In-lab Tracker\n\tSubject ID: {subject_id}\n\tSubmitter: {current_user.user_id} {'' if not current_user.first_name else f'({current_user.first_name})'}",
        credentials=flask_session["google_credentials"],
    )
    new_form = TrackerForm(
        form_owner=current_user.user_id, subject_id=subject_id, form_data=form_data, timestamp=db.func.now()
    )
    db.session.add(new_form)
    db.session.commit()

    return jsonify({"message": "Tracker form submitted successfully"}), 200


@api_bp.route("/data/action/confirm_tracker_form", methods=["POST"])
@login_required
def confirm_tracker_form():
    data = request.json
    form_id = data.get("form_id")
    form = TrackerForm.query.get(form_id)
    if not form:
        return jsonify({"error": "Form not found"}), 404
    form.validated = True
    form.form_validator = current_user.user_id
    db.session.commit()
    return jsonify({"message": "Form validated successfully"}), 200
