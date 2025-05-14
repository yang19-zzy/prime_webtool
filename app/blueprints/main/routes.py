# app/blueprints/main/routes.py

from flask import render_template, redirect, url_for, request, flash, session as flask_session
from . import main_bp

@main_bp.route('/')
def index():
    """
    Render the index page.
    """
    return render_template('index.html', title='Home')

@main_bp.route("/set-session")
def set_session():
    flask_session["init"] = "yes"
    return "Session set"

@main_bp.route('/get-session')
def get_session():
    return dict(flask_session)

@main_bp.route("/debug-url")
def debug_url():
    return request.url