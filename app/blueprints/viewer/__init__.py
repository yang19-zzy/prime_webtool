# app/blueprints/viewer/__init__.py
from flask import Blueprint

viewer_bp = Blueprint(
    "viewer",
    __name__,
    url_prefix="/data_viewer",
    template_folder="../../templates",
    static_folder="../../static",
)

from . import routes
