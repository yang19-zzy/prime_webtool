# app/blueprints/validator/__init__.py
from flask import Blueprint

validator_bp = Blueprint(
    "validator",
    __name__,
    url_prefix="/test_validator",
    template_folder="../../templates",
    static_folder="../../static",
)

from . import routes
