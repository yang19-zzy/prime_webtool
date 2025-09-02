# app/blueprints/tools/routes.py
import uuid
from werkzeug.utils import secure_filename
from flask import (
    current_app,
    flash,
    render_template,
    request,
    session as flask_session,
    jsonify,
    url_for,
    redirect,
    send_file,
)

from . import tools_bp
import base64
import json
import io
import os
import requests
from app.extensions import (
    db,
    get_s3,
    get_s3_bucket,
    get_s3_metadata
)
from app.models import PDFJob, UserActivity
# from app.extensions import get_lambda_client
from botocore.exceptions import ClientError
import datetime


@tools_bp.route("/")
def data_tools():
    return render_template("tools.html", title="Tools")


@tools_bp.route("/jobs", methods=["POST"])
def create_job():
    file = request.files.get("pdf-upload-test")
    if not file or file.filename == "":
        return jsonify({"message": "Invalid or missing PDF file."}), 400

    job_id = str(uuid.uuid4())
    try:
        # Single atomic transaction for job + activity
        with db.session.begin():
            new_job = PDFJob(job_id=job_id, status="queued", created_at=db.func.now())
            db.session.add(new_job)
            # user_activity = UserActivity(
            #     user_id=flask_session.get("user_id"),
            #     action="pdf_upload",
            #     timestamp=datetime.now(),
            # )
            # db.session.add(user_activity)

        s3 = get_s3()
        s3_bucket = get_s3_bucket()
        s3_metadata = get_s3_metadata()
        object_key = f"uploads/{job_id}.pdf"
        s3.upload_fileobj(
            file,
            s3_bucket,
            object_key,
            ExtraArgs={
                "Metadata": s3_metadata,
                "ContentType": "application/pdf" or file.mimetype,
                "ContentDisposition": f"attachment; filename={secure_filename(file.filename)}"
            }
        )

        resp = jsonify({"message": "Job created successfully", "job_id": job_id, "ok": True})
        resp.status_code = 201
        resp.headers["Location"] = url_for("tools.check_status", job_id=job_id, _external=True)
        return resp

    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({"error": f"Failed to create job: {str(e)}"}), 500
    
@tools_bp.route("/check-status/<job_id>")
def check_status(job_id):
    s3 = get_s3()
    s3_bucket = get_s3_bucket()
    file_key = f"download/{job_id}.csv"
    try:
        s3.head_object(Bucket=s3_bucket, Key=file_key)

        PDFJob.query.filter_by(job_id=job_id).update({
            "status": "completed",
            "completed_at": db.func.now(),
        })
        db.session.commit()
        return jsonify({"status": "completed", "job_id": job_id, "ok": True}), 200

    except ClientError as e:
        code = (e.response or {}).get("Error", {}).get("Code", "")
        if code in ("404", "NoSuchKey", "NotFound"):
            # Still processing
            resp = jsonify({"status": "processing", "job_id": job_id, "ok": True})
            # No cache headers
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"] = "no-cache"
            return resp, 202
        # Unexpected S3 error – surface message
        return jsonify({"status": "error", "message": str(e), "job_id": job_id, "ok": False}), 502

    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "job_id": job_id, "ok": False}), 500


@tools_bp.route("/download/<job_id>")
def download_file(job_id):
    try:
        s3 = get_s3()
        s3_bucket = get_s3_bucket()
        file_key = f"download/{job_id}.csv"

        # Generate a presigned URL for the S3 object
        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": s3_bucket,
                "Key": file_key,
                "ResponseContentDisposition": f"attachment; filename=\"{job_id}.csv\"",
                "ResponseContentType": "application/csv",
            },
            ExpiresIn=3600,  # 1 hour
        )

        PDFJob.query.filter_by(job_id=job_id).update({
            "download_url": presigned_url,
            "expired_in": 3600,
        })
        db.session.commit()
        return jsonify({"download_url": presigned_url, "job_id": job_id, "expires_in": 3600, "ok": True}), 200

    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({"error": str(e), "ok": False}), 500
