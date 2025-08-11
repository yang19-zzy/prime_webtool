# app/blueprints/main/__init__.py
from flask import Blueprint

main_bp = Blueprint(
    "main",
    __name__,
    url_prefix="/",
    template_folder="../../templates",
    static_folder="../../static",
)

from . import routes
