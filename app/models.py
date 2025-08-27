# app/models.py

from app.extensions import db
from sqlalchemy import UniqueConstraint
from flask_login import UserMixin

class FormOptions(db.Model):
    __tablename__ = "form_options"

    row_id = db.Column(db.Integer, primary_key=True)
    field_name = db.Column(db.String(100), nullable=False)
    item_num = db.Column(db.Integer, nullable=True)
    value = db.Column(db.String(255), nullable=False)


class TableColumns(db.Model):
    __tablename__ = "table_columns"
    __table_args__ = (
        UniqueConstraint(
            "table_name", "column_name", "data_source", name="uq_table_columns"
        ),
        {"schema": "backend"},
    )

    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False)
    column_name = db.Column(db.String(100), nullable=False)
    data_source = db.Column(db.String(100), nullable=False)


class MergeHistory(db.Model):
    __tablename__ = "merge_history"
    __table_args__ = {"schema": "backend"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    selected_tables = db.Column(db.JSON, nullable=False)
    merged_key = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)


class TrackerForm(db.Model):
    __tablename__ = "tracker_form"
    __table_args__ = {"schema": "backend"}

    id = db.Column(db.Integer, primary_key=True)
    form_owner = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.String(100), nullable=False)
    form_data = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    form_validator = db.Column(db.String(100), nullable=False)
    validated = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<TrackerForm {self.id}>"


class UserRole(db.Model):
    __tablename__ = "user_role"
    __table_args__ = (
        UniqueConstraint("user_id", "role", name="user_role_pkey"),
        {"schema": "backend"},
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    in_lab_user = db.Column(db.Boolean, default=False)  #used for toggle button

    def __repr__(self):
        return f"<UserRole {self.user_id} - {self.role}>"


class User(db.Model, UserMixin):
    __tablename__ = "user"
    __table_args__ = {"schema": "backend"}

    row_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"<User {self.email}>"


class PDFJob(db.Model):
    __tablename__ = "pdf_jobs"
    __table_args__ = {"schema": "backend"}

    job_id = db.Column(db.String(100), primary_key=True)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    download_url = db.Column(db.String(255), nullable=True)
    expired_in = db.Column(db.Integer, nullable=True, default=3600)  # seconds

    def __repr__(self):
        return f"<PDFJob {self.job_id}>"
    

class UserActivity(db.Model):
    __tablename__ = "user_activity"
    __table_args__ = {"schema": "backend"}

    row_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    request_path = db.Column(db.String(255), nullable=False)
    request_method = db.Column(db.String(10), nullable=False)
    request_ip = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return f"<UserActivity {self.row_id} - {self.user_id} - {self.action}>"
    

class SchemaAccess(db.Model):
    __tablename__ = "schema_access"
    __table_args__ = {"schema": "backend"}

    row_id = db.Column(db.Integer, primary_key=True)
    schema_name = db.Column(db.String(100), nullable=False)
    limited_access = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<SchemaAccess {self.schema_name} - {self.limited_access}>"