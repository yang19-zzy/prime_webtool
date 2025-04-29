# app/blueprints/tracker/routes.py
from flask import render_template, request, session as flask_session, jsonify, url_for
# from app.extensions import google, s3, s3_bucket
from app.utils.emailer import send_email
from app.utils.option_loader import load_form_options
from app.models import TrackerForm
from app.extensions import db
from . import tracker_bp
# from app.config import DEVICES, BODY_PARTS, TEST_TYPES, VISIT_NUMS

@tracker_bp.route('/')
def test_tracker():
    print('debugging----------:', flask_session.get('user_info'))
    # if not session.get('user_info'):
    #     return redirect('/auth/login')
    return render_template('test_tracker.html', title="Test Tracker")

@tracker_bp.route('/submit_data', methods=['POST'])
def submit_data():
    if not flask_session.get('user_info'):
        return jsonify({'error': 'Unauthorized, no user-info, need login'}), 401

    # Parse JSON data from the request
    form_data = request.get_json()
    if not form_data:
        return jsonify({'error': 'Invalid data'}), 400

    # Extract metadata and devices
    metadata = form_data.get('metadata', {})
    devices = form_data.get('devices', [])

    print("Metadata:", metadata)
    print("Devices:", devices)

    # Example: Send an email notification
    form_owner = metadata.get('form_owner') or flask_session['user_info'].get('user_id')
    subject_id = metadata.get('subject_id')
    print(form_data)

    # Save the form data to the database
    new_form = TrackerForm(
        form_owner=form_owner,
        subject_id=subject_id,
        form_data=form_data
    )
    db.session.add(new_form)
    db.session.commit()

    send_email(
        recipient="zzyang@umich.edu",
        subject="New Form Submitted [Test]!!!",
        message_text=f"Test Tracker: {subject_id} has been submitted by {form_owner}"
    )

    # Return success message as JSON
    return jsonify({'message': 'Form data submitted successfully!'})


@tracker_bp.route('/select_options', methods=['GET'])
def get_select_options():
    if not flask_session.get('user_info'):
        return jsonify({'error': 'Unauthorized, no user-info, need login'}), 401

    return jsonify(load_form_options())
