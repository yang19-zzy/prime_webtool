# app/blueprints/tools/routes.py
from flask import flash, render_template, request, session as flask_session, jsonify, url_for, redirect, send_file
# from app.extensions import get_lambda_client
from . import tools_bp
import base64
import json
import io
import os
import requests


@tools_bp.route('/')
def data_tools():
    error = flask_session.pop('error', None)
    csv_data = flask_session.pop('csv_data', None)
    return render_template('tools.html', title="Tools", error=error, csv_data=csv_data)



@tools_bp.route('/extract_pdf', methods=['POST'])
def extract_pdf():
    try:
        file = request.files.get('pdf-upload')
        if not file or file.filename == '':
            flask_session['error'] = "Invalid or missing PDF file."
            return redirect(url_for('tools.data_tools'))

        file_bytes = file.read()
        encoded_pdf = base64.b64encode(file_bytes).decode('utf-8')

        lambda_url = os.environ.get('AWS_LAMBDA_PDF_EXTRACT')
        if not lambda_url:
            flask_session['error'] = "Lambda URL not configured."
            return redirect(url_for('tools.data_tools'))

        lambda_response = requests.post(
            lambda_url,
            json={"file_data": encoded_pdf, "filename": file.filename},
            headers={"Content-Type": "application/json"}
        )

        if lambda_response.status_code != 200:
            flask_session['error'] = "Failed to process file. Try again later."
            return redirect(url_for('tools.data_tools'))

        result = lambda_response.json()
        csv_string = result.get('csv_data')
        if not csv_string:
            flask_session['error'] = "No CSV data returned. Please check the PDF file."
            return redirect(url_for('tools.data_tools'))

        flask_session['csv_data'] = csv_string
        return redirect(url_for('tools.data_tools'))

    except Exception as e:
        flask_session['error'] = f"An unexpected error occurred: {str(e)}"
        return redirect(url_for('tools.data_tools'))
