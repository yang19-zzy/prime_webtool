# blueprints/viewer/routes.py
from . import viewer_bp
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session as flask_session,
    make_response,
    jsonify,
    current_app,
)

# from app.extensions import get_s3, get_s3_bucket,
from app.extensions import get_redis, db
from app.utils.data_parser import prefix_to_json

# from app.utils.s3_fetcher import get_s3_data, list_prefix, get_session_data
from app.utils.storage_tool import get_redis
from app.utils.merge_q_generator import merge_q_generator
from app.models import TableColumns, MergeHistory
from collections import defaultdict
import pandas as pd
import hashlib
import time
import json
from sqlalchemy import text


@viewer_bp.route("/")
def data_viewer():
    return render_template("data_viewer.html")


# @viewer_bp.route('/options', methods=['GET'])
# def get_data_viewer_options():
#     '''get data source options from S3 bucket and get the table names'''
#     if not flask_session.get('user_info'):
#         return jsonify({'error': 'Unauthorized'}), 401

#     if not get_s3():
#         return jsonify({'error': 'S3 connection failed'}), 500

#     try:
#         prefixes = list_prefix(s3=get_s3(), bucket=get_s3_bucket())
#         print('prefixes:', prefixes)
#         sources = [prefix.strip('/') for prefix in prefixes]
#         sources = prefix_to_json(sources)
#         return jsonify(sources)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


@viewer_bp.route("/table_options", methods=["POST", "GET"])
def get_table_options():
    if not flask_session.get("user_info"):
        return jsonify({"error": "Unauthorized"}), 401

    options = TableColumns.query.order_by(
        TableColumns.id, TableColumns.data_source, TableColumns.table_name
    ).all()
    grouped = defaultdict(lambda: defaultdict(list))
    for opt in options:
        grouped[opt.data_source][opt.table_name].append(opt.column_name)
    # print('grouped:', grouped)
    return jsonify({"data_source": grouped})


@viewer_bp.route("/merge", methods=["POST", "GET"])
def merge_data():
    if not flask_session.get("user_info"):
        return jsonify({"error": "Unauthorized"}), 401

    # Get the data from the request
    data = request.get_json()
    print("Received merge request:", data)

    # key_raw = f"{str(time.time())}_{str(data)}"
    key_raw = str(
        data
    )  # reuse the key the the same set of selected tables retrieved again in the same session
    key = hashlib.md5(key_raw.encode()).hexdigest()

    r = get_redis()
    df_merged = r.get(key)

    # Check if the merged data already exists in Redis
    if df_merged:
        return jsonify({"message": "Data already merged", "key": key})

    q = merge_q_generator(data, db)
    if not q:
        return jsonify({"error": "No data to merge"}), 400

    print("Generated SQL Join Query:", q)
    df_merged = pd.read_sql(text(q), con=db.engine)
    # df_merged = df_merged.astype(str)  # Convert all columns to string type

    # Save the merged dataframe to Redis
    r.set(f"merged_{key}", json.dumps(df_merged.to_json(orient="records")))

    # track user activity
    history = MergeHistory(
        user_id=flask_session.get("user_info").get("user_id"),
        merged_key=f"merged_{key}",
        selected_tables=json.dumps(data),
        # timestamp=time.time()
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({"message": "Data merged successfully", "key": f"merged_{key}"})


@viewer_bp.route("/download/<key>", methods=["GET"])
def download_merged_data(key):
    r = get_redis()
    value = r.get(key)
    if not value:
        return jsonify({"error": "No data found"}), 404
    return jsonify({"data": json.loads(value)})
