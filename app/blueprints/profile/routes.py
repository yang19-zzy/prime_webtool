#app/blueprints/profile/routes.py
from flask import render_template, request, jsonify, current_app, session as flask_session
from flask_login import login_required, current_user

from . import profile_bp

@profile_bp.route("/load", methods=["GET"])
@login_required
def load_profile():
    return render_template('profile.html')
