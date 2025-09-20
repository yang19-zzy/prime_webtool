# app/dash_app/callbacks.py
from dash import Output, Input, State, dcc
from dash.exceptions import PreventUpdate
from dash import html, dash_table

# import redis
from app.extensions import get_redis
import json
import csv
from io import StringIO
# import pandas as pd


def register_callbacks(app):
    @app.callback(Output("table-container", "children"), Input("url", "pathname"))
    def display_table(pathname):
        if not pathname or not pathname.startswith("/dash_viewer/"):
            raise PreventUpdate

        key = pathname.replace("/dash_viewer/", "")
        # print('this is pathname', pathname)
        # print(key)
        if not key:
            raise PreventUpdate

        r = get_redis()
        value = r.get(key)
        if not value:
            return html.Div("Data not found... why!!!??????")

        try:
            if isinstance(value, bytes):
                data = json.loads(value.decode("utf-8"))
            else:
                data = json.loads(value)
        except (json.JSONDecodeError, ValueError) as e:
            return html.Div(f"Error loading data: {str(e)}")

        return dash_table.DataTable(
            id="merged-table",
            columns=[{"name": i, "id": i} for i in data[0].keys()],
            data=data,
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "5px"},
            filter_action="native",
            sort_action="native",
        )

    @app.callback(
        Output("download-dataframe-xlsx", "data"),
        Input("btn-download", "n_clicks"),
        State("merged-table", "derived_virtual_data"),
        prevent_initial_call=True,
    )
    def download_table(n_clicks, filtered_data):
        # if not filtered_data:
        #     raise PreventUpdate
        # df = pd.DataFrame(filtered_data)
        # return dcc.send_data_frame(df.to_excel, "data.xlsx", index=False)
        """
        Produce an in-memory CSV file (UTF-8 with BOM for Excel compatibility)
        from a list-of-dicts (filtered_data) without using pandas.
        Returns bytes via dcc.send_bytes so Dash triggers a file download.
        """
        if not filtered_data:
            raise PreventUpdate

        # Use keys from the first row as header order
        headers = list(filtered_data[0].keys())

        # Write CSV to a text buffer, then encode with UTF-8 BOM so Excel opens correctly
        s = StringIO()
        writer = csv.writer(s)
        writer.writerow(headers)
        for row in filtered_data:
            writer.writerow([row.get(h, "") for h in headers])

        csv_bytes = s.getvalue().encode("utf-8-sig")
        return dcc.send_bytes(lambda f: f.write(csv_bytes), "data.csv")
