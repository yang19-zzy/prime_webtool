# app/blueprints/tools/routes.py
from flask import render_template, request, session as flask_session, jsonify, url_for, redirect, send_file
# from app.extensions import get_lambda_client
from . import tools_bp
import base64
import json
import io
import os
import requests


@tools_bp.route('/')
def data_tools():
    print('debugging----------:', flask_session.get('user_info'))
    if not flask_session.get('user_info'):
        return redirect(url_for('auth.auth_login'))
    return render_template('tools.html', title="Test Tools")



@tools_bp.route('/extract_pdf', methods=['POST'])
def extract_pdf():
    if 'pdf-upload' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["pdf-upload"]
    if file and file.filename.endswith('.pdf'):
        file_bytes = file.read()
        encoded_pdf = base64.b64encode(file_bytes).decode('utf-8')

        # payload = json.dumps({
        #     "file_data": encoded_pdf,
        #     "filename": file.filename
        # })
        # return jsonify({"message": "File received, processing...", "payload": payload}), 202

        # lambda_client = get_lambda_client()
        # lambda_response = lambda_client.invoke(
        #     FunctionName='pdf_extractor',
        #     InvocationType='RequestResponse',
        #     Payload=json.dumps(payload).encode('utf-8')
        # )
        lambda_url = os.environ.get('AWS_LAMBDA_PDF_EXTRACT')
        print('Lambda URL:', lambda_url, "file:", file.filename)
        if not lambda_url:
            return jsonify({"error": "Lambda URL not configured"}), 5
        lambda_response = requests.post(
            lambda_url, 
            json={"file_data": encoded_pdf, "filename": file.filename},
            headers={"Content-Type": "application/json"}
        )

        if lambda_response.status_code != 200:
            return jsonify({"error": "Failed to invoke Lambda function", "details": lambda_response.text, "lambda_url": lambda_url}), 500

        result = lambda_response.json()
        csv_string = result.get('csv_data')
        csv_bytes = base64.b64decode(csv_string)
        return send_file(
            io.BytesIO(csv_bytes),
            mimetype='text/csv',
            as_attachment=True,
            download_name='extracted_data.csv'
        )
    
    return jsonify({"error": "Invalid file type"}), 400

    
    # # Process each file (dummy processing for now)
    # extracted_data = []
    # for file in files:
    #     if file and file.filename.endswith('.pdf'):
    #         # Here you would add your PDF extraction logic
    #         extracted_data.append({"filename": file.filename, "status": "extracted"})
    
    # return jsonify({"status": "success", "data": extracted_data}), 200