# app/blueprints/tracker/__init__.py
from flask import Blueprint

tracker_bp = Blueprint('tracker', __name__, url_prefix='/test_tracker', template_folder='../../templates', static_folder='../../static')

from . import routes