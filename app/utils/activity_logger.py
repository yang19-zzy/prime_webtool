# app/utils/activity_logger.py
from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from datetime import datetime
from flask import request, has_request_context, session as flask_session
from app.models import UserActivity

def register_activity_hooks(db):
    @event.listens_for(Session, "after_flush")
    def _after_flush(session, flush_context):
        if session.info.get("suppress_activity"):
            return
        rows = session.info.setdefault("activity_rows", [])
        for obj in session.new:
            if isinstance(obj, UserActivity):
                continue
            rows.append(_build_activity(obj, "insert"))
        for obj in session.dirty:
            if isinstance(obj, UserActivity):
                continue
            if inspect(obj).attrs:
                rows.append(_build_activity(obj, "update"))
        for obj in session.deleted:
            if isinstance(obj, UserActivity):
                continue
            rows.append(_build_activity(obj, "delete"))

    @event.listens_for(Session, "before_commit")
    def _before_commit(session):
        rows = session.info.pop("activity_rows", None)
        if not rows:
            return
        session.info["suppress_activity"] = True
        try:
            session.add_all(rows)
        finally:
            session.info["suppress_activity"] = False


def _build_activity(obj, action):
    meta = _req_meta()
    return UserActivity(
        user_id=flask_session.get("user_id", "anonymous"),
        action=action,
        timestamp= datetime.now(),
        request_path=meta.get("path"),
        request_method=meta.get("method"),
        request_ip=meta.get("ip"),
    )

def _req_meta():
    if not has_request_context():
        return {}
    return {
        "path": request.path,
        "method": request.method,
        "ip": request.remote_addr
    }