# app/blueprints/main/routes.py

from flask import render_template, redirect, url_for, request, flash
from . import main_bp

@main_bp.route('/')
def index():
    """
    Render the index page.
    """
    return render_template('index.html', title='Home')