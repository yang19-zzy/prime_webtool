# app/blueprints/api/routes.py
from app.utils.merge_q_generator_new import merge_q_generator_new
from . import api_bp
from flask import (
    request,
    session as flask_session,
    jsonify,
    current_app
)
from flask_login import current_user, login_required
from app.extensions import db, get_redis, get_email_list, get_s3, get_s3_bucket, get_s3_metadata
from app.models import MergeHistory
from app.utils.data_retriever import *
from app.utils.merge_q_generator import merge_q_generator
from app.utils.emailer import send_email
from sqlalchemy import text

import base64
from datetime import date, datetime
from decimal import Decimal
import json
import uuid
from io import BytesIO
from werkzeug.utils import secure_filename


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
    # user = UserRole.query.filter_by(user_id=user_id).first()
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    user.in_lab_user = not user.in_lab_user
    db.session.commit()
    return jsonify({"message": "User in-lab status updated"}), 200

@api_bp.route("/admin/group_project_access", methods=["GET"])
@login_required
def list_projects():
    groups, projects = get_group_project_access()
    return jsonify({"groups": groups, "projects": projects}), 200

@api_bp.route("/admin/change_user_access", methods=["POST"])
@login_required
def change_user_access():
    """Admin can change user's group access and tool/feature access."""
    data = request.json
    for user in data['changed_users']:
        user_id = user.get("user_id")
        new_group_id = user.get("group_id")
        in_lab_user = user.get("in_lab_user", False)
        user = User.query.filter_by(user_id=user_id).first()
        user_group = UserGroups.query.filter_by(user_id=user_id).first()
        if user and not user_group: # if user exists but no group, create new group entry
            user_group = UserGroups(user_id=user_id, group_id=new_group_id, added_at=datetime.now())
            db.session.add(user_group)
        elif user and user_group: # if user and group both exist, update group
            user_group.group_id = new_group_id
        if user:
            user.in_lab_user = in_lab_user
    db.session.commit()
    return jsonify({"message": "User access updated"}), 200

@api_bp.route("/admin/create_group", methods=["POST"])
@login_required
def create_group():
    data = request.json
    group_name = data.get("group_name")
    group_desc = data.get("group_desc", "")
    projects = data.get("projects", "")
    if not group_name:
        return jsonify({"message": "Group name is required"}), 400
    new_group = Groups(group_abbr=group_name, group_desc=group_desc, created_on=datetime.now(), included_projects=projects)
    db.session.add(new_group)
    db.session.commit()
    return jsonify({"message": "Group created", "group_id": new_group.group_id}), 201


# Data Retrieval
@api_bp.route("/data/get/table_options", methods=["GET"])
@login_required
def table_options():
    options = get_table_options(current_user.user_id)
    # return jsonify({"table_select_options": options}), 200
    return jsonify({"message": "This endpoint is deprecated. Please use /data/get/data_viewer/init instead."}), 410


@api_bp.route("/data/get/tracker_options", methods=["GET"])
@login_required
def tracker_options():
    options = get_tracker_options(current_user.user_id)
    return jsonify({"tracker_select_options": options}), 200

@api_bp.route("/v2/data/form", methods=["GET"])
@login_required
def form_options():
    options = get_form_options()
    return jsonify({"form_options": options}), 200

@api_bp.route("/data/get/unvalidated_forms", methods=["GET"])
@login_required
def unvalidated_forms():
    forms = get_unvalidated_forms(current_user.user_id)
    return jsonify({"unvalidated_forms": forms}), 200


@api_bp.route("/data/get/tables_desc/<proj>", methods=["GET"])
@login_required
def tables_desc(proj):
    tables_description = get_tables_description(proj)
    return jsonify({"tables_description": tables_description}), 200


@api_bp.route("/data/get/merge_result/<key>", methods=["GET"])
@login_required
def get_merge_result(key):
    redis_client = get_redis()
    raw = redis_client.get(key)
    if raw is None:
        merged_data = []
    else:
        merged_data = json.loads(raw.decode("utf-8"))
    return jsonify({
        "merged_data": merged_data,
        "column_orders": list(merged_data[0].keys()) if merged_data else []
        }), 200

@api_bp.route("/data/get/config", methods=["GET"])
@login_required
def get_config():
    return jsonify({
        "data_documentation_url": current_app.config.get('DATA_VIEWER_DOCS_URL')
    }), 200

@api_bp.route("/data/action/merge_with_key_cols", methods=["POST"])
@login_required
def merge_with_key_cols():
    data = request.json
    merged_key, final_sql_query = merge_q_generator_new(data)
    redis_key = f"merged_data:{merged_key}"
    redis_client = get_redis()
    if not redis_client.exists(redis_key):  # if not in cache, query and store
        result = db.session.execute(text(final_sql_query))
        merged_data = [dict(row._mapping) for row in result.fetchall()]

        serialized = json.dumps(merged_data, default=_json_serializer, sort_keys=False)
        redis_client.setex(redis_key, 3600, serialized)
    else:
        raw = redis_client.get(redis_key)
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
    return jsonify({"message": "Merge successful", "redis_key": redis_key, 'query': final_sql_query}), 200


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

# Tools Actions
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

@api_bp.route("/v2/data/action/submit_tracker_form", methods=["POST"])
@login_required
def v2_submit_tracker_form():
    form_data = request.get_json()
    metadata = form_data.get("metadata", {})
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

@api_bp.route("/v2/data/action/confirm_tracker_form", methods=["POST"])
@login_required
def v2_confirm_tracker_form():
    data = request.get_json()
    form_id = data.get("form_id")
    updated_by = data.get("user_id", current_user.user_id)
    form = TrackerForm.query.get(form_id)
    if not form:
        return jsonify({"error": "Form not found"}), 404
    form.validated = True
    form.form_validator = updated_by
    db.session.commit()
    return jsonify({"message": "Form validated successfully"}), 200


@api_bp.route("/data/action/send_contact_email", methods=["POST"])
@login_required
def send_contact_email():
    data = request.json
    recipient = data.get("recipient")
    subject = data.get("subject")
    message_text = data.get("message_text")

    send_email(
        recipient=recipient,
        subject=subject,
        message_text=message_text,
        credentials=flask_session["google_credentials"],
    )
    return jsonify({"message": "Contact email sent successfully"}), 200

@api_bp.route("/v2/data/action/map_fmri", methods=["POST"])
@login_required
def map_fmri():
    # Get the uploaded file from the form
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file extension
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({"error": "Only Excel files are allowed"}), 400
    
    # Logic to call AWS Lambda for fMRI mapping
    s3 = get_s3()
    s3_bucket = get_s3_bucket()
    
    try:
        job_id = str(uuid.uuid4())
        
        # Read file content and wrap in BytesIO
        file_content = file.read()
        file_obj = BytesIO(file_content)
        
        s3.upload_fileobj(
            Fileobj=file_obj,
            Bucket=s3_bucket,
            Key=f"uploads/{job_id}.xlsx",
            ExtraArgs={
            "Metadata": get_s3_metadata(),
            "ContentType": file.content_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            "ContentDisposition": f"attachment; filename={secure_filename(file.filename)}"
            }
        )
        

        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": s3_bucket,
                "Key": f"download/{job_id}.xlsx",
                "ResponseContentDisposition": f"attachment; filename=\"{job_id}.xlsx\"",
                "ResponseContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
            ExpiresIn=3600,  # 1 hour
        )

        return jsonify({
            "message": "fMRI mapping initiated",
            "job_id": job_id,
            "presigned_url": presigned_url
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        

# Data Viewer Static Page
@api_bp.route("/data/get/data_viewer/init", methods=["GET"])
@login_required
def data_viewer_init():
    table_options = get_column_options(current_user.user_id)
    projects = table_options.keys()
    tables_description = {proj:  get_tables_description(proj) for proj in projects}
    return jsonify({
        "projects": list(projects),
        "table_select_options": table_options,
        "tables_description": tables_description,
    }), 200
