# app/blueprints/auth/routes.py
from . import auth_bp
from flask import request, redirect, url_for, session as flask_session, make_response, jsonify
from app.extensions import get_google, db
from sqlalchemy import text

@auth_bp.route('/login')
def auth_login():
    next_url = request.args.get('next', request.referrer or url_for('/'))
    flask_session['next_url'] = next_url
    redirect_uri = url_for('auth.auth_callback', _external=True)
    return get_google().authorize_redirect(redirect_uri, state=next_url)

@auth_bp.route('/oauth2callback')
def auth_callback():
    token = get_google().authorize_access_token()
    user_info = token.get('userinfo')
    if user_info['email']:
        user_info['user_id'] = user_info['email'].split('@')[0]
        print('this is user-id???????:', user_info['user_id'])
        user_info['is_active'] = True
        user_info['is_authenticated'] = True
        user_info['is_anonymous'] = False
    flask_session['user_info'] = user_info
    flask_session.permanent = True
    print('this is user-info!!!!!!!!!:', user_info)

    next_url = flask_session.pop('next_url', request.args.get('state', '/'))
    response = make_response(redirect(next_url))
    response.set_cookie('logged_in', 'true', max_age=60*60, httponly=False, secure=True)
    return response

@auth_bp.route('/logout')
def auth_logout():
    # Clear user session and cookies
    next_url = request.args.get('state') or request.referrer or '/'
    flask_session.clear()
    response = make_response(redirect(next_url))
    response.delete_cookie('logged_in')
    return response


@auth_bp.route('/db_test', methods=['GET'])
def db_test():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({'status': 'Aurora connected successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500