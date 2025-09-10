#app/blueprints/profile/routes.py
from flask import render_template
from flask_login import login_required

from . import profile_bp

@profile_bp.route("/load_profile", methods=["GET"])
# @login_required
def load_profile():
    return render_template('profile.html')
