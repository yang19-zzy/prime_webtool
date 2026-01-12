# app/blueprints/viewer/__init__.py
from flask import Blueprint

viewer_bp_new = Blueprint(
    "viewer_new",
    __name__,
    url_prefix="/data_viewer_new",
    template_folder="../../templates",
    static_folder="../../static",
)

from . import routes
