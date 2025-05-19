from app import create_app, models

from flask import render_template, jsonify, request, session as flask_session
from flask_login import LoginManager

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd



app= create_app()
login_manager = LoginManager(app)
login_manager.login_view = 'auth_login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"
login_manager.session_protection = "strong"

@login_manager.user_loader
def load_user(user_id):
    user_info = flask_session.get('user_info')
    if user_info:
        return models.User(user_info['email'].split('@')[0], user_info['name'], user_info['email'])
    return None




if __name__ == "__main__":
    app.run(debug=True)
    