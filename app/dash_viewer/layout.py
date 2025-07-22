# app/dash_app/layout.py
from dash import html, dcc, dash_table
import pandas as pd
import json
import redis

def create_layout():
    return html.Div([
        dcc.Location(id='url', refresh=True),
        html.Div(id='table-container'),
        dcc.Loading(
            id="loading-download",
            type="default",
            children=[
                html.Button("Download Current View", id="btn-download", n_clicks=0, className="btn"),
                dcc.Download(id="download-dataframe-xlsx")
            ]
        )
    ])