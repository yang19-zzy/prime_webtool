# app/blueprints/validator/routes.py
from flask import render_template, request, session as flask_session, jsonify, url_for
from app.models import TrackerForm, UserRole
from app.extensions import db, get_redis
from . import validator_bp
import json

@validator_bp.route('/')
def validate():
    if not flask_session.get('user_info'):
        flask_session['user_info'] = None
    else:
        # user_info = flask_session['user_info']
        # user_role = UserRole.query.filter_by(user_id=flask_session['user_id']).first().role
        # flask_session['user_role'] = user_role
        print(flask_session['user_role'])
    return render_template('test_validator.html', title="Test Validator")



@validator_bp.route('/get_unvalidated_forms', methods=['GET'])
def get_unvalidated_forms():
    
    if not flask_session.get('user_info'):
        return jsonify({'error': 'Unauthorized, no user-info, need login'}), 401
    
    try:
        need_validation = TrackerForm.query.filter_by(validated=False).all()
        data = [{
            'form_id': f.id,
            "data": {
            'form_owner': f.form_owner,
            'subject_id': f.subject_id,
            'form_data': f.form_data,
            'form_validator': f.form_validator,
            'validated': f.validated
        }} for f in need_validation]
        print(data)
    except Exception as e:
        print(f"Error fetching unvalidated forms: {e}")
        return jsonify({'error': 'Failed to fetch unvalidated forms'}), 500
    return jsonify({'data': data}), 200



@validator_bp.route('/reset_cache')
def reset_cache():
    r = get_redis()
    if not r:
        return jsonify({'error': 'Redis connection failed'}), 500
    
    if not flask_session.get('user_info'):
        return jsonify({'error': 'Unauthorized, no user-info, need login'}), 401
    
    r.delete('unvalidated_forms')
    return jsonify({'message': 'Cache reset successfully!'}), 200



@validator_bp.route('/confirm_form', methods=['POST'])
def confirm_form():
    if not flask_session.get('user_info'):
        return jsonify({'error': 'Unauthorized, login required'}), 401

    data = request.get_json()
    form_id = data.get('form_id')
    if not form_id:
        return jsonify({'error': 'form_id missing in request'}), 400

    form = TrackerForm.query.get(form_id)
    if not form:
        return jsonify({'error': 'Form not found'}), 404

    form.validated = True
    form.form_validator = flask_session['user_info']['user_id']
    db.session.commit()

    next_url = url_for('validator.get_unvalidated_forms')
    return jsonify({'message': 'Form confirmed and updated'}), 200
