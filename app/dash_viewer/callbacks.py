# app/dash_app/callbacks.py
from dash import Output, Input, State, dcc
from dash.exceptions import PreventUpdate
from dash import html, dash_table
# import redis
from app.utils.storage_tool import get_redis
import json
import pandas as pd

def register_callbacks(app):
    @app.callback(
        Output('table-container', 'children'),
        Input('url', 'pathname')
    )
    def display_table(pathname):
        if not pathname or not pathname.startswith('/dash_viewer/'):
            raise PreventUpdate

        key = pathname.replace('/dash_viewer/', '')
        if not key:
            raise PreventUpdate

        r = get_redis()
        value = r.get(key)
        if not value:
            return html.Div("Data not found")

        df = pd.DataFrame(json.loads(json.loads(value)))  # double decode due to how you saved
        return dash_table.DataTable(
            id='merged-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            filter_action='native',
            sort_action='native',
        )
    
    @app.callback(
        Output("download-dataframe-xlsx", "data"),
        Input("btn-download", "n_clicks"),
        State("merged-table", "derived_virtual_data"),
        prevent_initial_call=True,
    )
    def download_table(n_clicks, filtered_data):
        if not filtered_data:
            raise PreventUpdate
        df = pd.DataFrame(filtered_data)
        return dcc.send_data_frame(df.to_excel, "data.xlsx", index=False)