# app/blueprints/profile/__init__.py
from flask import Blueprint

profile_bp = Blueprint(
    "profile",
    __name__,
    url_prefix="/profile",
)

from . import routes
