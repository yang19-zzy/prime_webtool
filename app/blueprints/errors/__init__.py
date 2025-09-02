# app/blueprints/errors/__init__.py
from flask import Blueprint

errors_bp = Blueprint(
    "errors",
    __name__,
    template_folder="../../templates",
    static_folder="../../static",
)

from . import routes
