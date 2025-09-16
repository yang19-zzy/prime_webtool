# blueprints/viewer/routes.py
from . import viewer_bp
from flask import render_template


@viewer_bp.route("/")
def data_viewer():
    return render_template("data_viewer.html")