# app/blueprints/auth/routes.py
from . import auth_bp
from flask import request, redirect, url_for, session as flask_session, make_response, jsonify
from app.extensions import get_google_flow, db
from app.models import User
from sqlalchemy import text
import requests

@auth_bp.route('/login')
def auth_login():
    next_url = request.args.get('next', request.referrer or url_for('/'))
    flask_session['next_url'] = next_url
    redirect_uri = url_for('auth.auth_callback', _external=True)
    # return get_google().authorize_redirect(redirect_uri, state=next_url)

    authorization_url, state = get_google_flow().authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=next_url
    )
    flask_session['state'] = state
    print('this is authorization_url:', authorization_url)
    print('this is state:', state)
    print('this is redirect_uri:', redirect_uri)
    return redirect(authorization_url)

@auth_bp.route('/oauth2callback')
def auth_callback():
    # token = get_google().authorize_access_token()
    flow = get_google_flow()
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    flask_session['google_credentials'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    # flask_session['google_credentials'] = creds  #throws error of "TypeError: Object of type Credentials is not JSON serializable"
    userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo'
    resp = requests.get(
        userinfo_endpoint,
        headers={'Authorization': f'Bearer {creds.token}'}
    )
    user_info = resp.json()
    user_info['user_id'] = user_info['email'].split('@')[0]
    flask_session['user_info'] = user_info


    # Check if the user is already in the database
    # If not, create a new user
    user = User.query.filter_by(username=user_info['user_id']).first()
    if not user:
        user = User(
            email=user_info['email'],
            username=user_info['user_id'],
            first_name=user_info['given_name'],
            last_name=user_info['family_name'],
        )
        db.session.add(user)
        db.session.commit()

    # if user_info['email']:
    #     user_info['user_id'] = user_info['email'].split('@')[0]
    #     print('this is user-id???????:', user_info['user_id'])
    #     user_info['is_active'] = True
    #     user_info['is_authenticated'] = True
    #     user_info['is_anonymous'] = False
    # flask_session['user_info'] = user_info
    # flask_session.permanent = True
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
    