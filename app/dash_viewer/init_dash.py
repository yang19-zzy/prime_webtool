# app/dash_app/init_dash.py
from dash import Dash
from app.dash_viewer.layout import create_layout
from app.dash_viewer.callbacks import register_callbacks

def init_dash(server):
    dash_app = Dash(
        __name__,
        server=server,
        url_base_pathname='/dash_viewer/',
        suppress_callback_exceptions=True
    )
    dash_app.title = "Dash Data Viewer"
    dash_app.layout = create_layout()
    register_callbacks(dash_app)