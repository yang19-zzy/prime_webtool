# app/blueprints/tools/__init__.py
from flask import Blueprint

tools_bp = Blueprint(
    "tools",
    __name__,
    url_prefix="/data_tools",
    template_folder="../../templates",
    static_folder="../../static",
)

from . import routes
