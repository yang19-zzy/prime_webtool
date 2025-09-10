# app/blueprints/auth/routes.py
from . import auth_bp
from flask import (
    request,
    redirect,
    url_for,
    session as flask_session,
    make_response,
    jsonify,
    render_template,
    current_app,
)
from flask_login import login_user, logout_user, current_user
from app.extensions import get_google_flow, db, get_email_list, login_manager
from app.models import User, UserRole
from sqlalchemy import text, inspect
import requests
import os


@auth_bp.route("/login")
def auth_login():
    next_url = request.args.get("next", request.referrer or url_for("main.index"))
    flask_session["next_url"] = next_url
    redirect_uri = url_for("auth.auth_callback", _external=True)

    authorization_url, state = get_google_flow().authorization_url(
        access_type="offline", include_granted_scopes="true", state=next_url
    )
    flask_session["state"] = state
    print("this is authorization_url:", authorization_url)
    print("this is state:", state)
    print("this is redirect_uri:", redirect_uri)
    return redirect(authorization_url)


@auth_bp.route("/oauth2callback")
def auth_callback():
    try:
        # Forcefully dispose stale connections (optional extra)
        db.engine.dispose()

        # token = get_google().authorize_access_token()
        flow = get_google_flow()
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        flask_session["google_credentials"] = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }
        # flask_session['google_credentials'] = creds  #throws error of "TypeError: Object of type Credentials is not JSON serializable"
        userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
        resp = requests.get(
            userinfo_endpoint, headers={"Authorization": f"Bearer {creds.token}"}
        )
        user_info = resp.json()
        user_info["user_id"] = user_info["email"].split("@")[0]
        flask_session["user_info"] = user_info
        flask_session["user_id"] = user_info["user_id"]

        try:
            # Check if the user is already in the database
            # If not, create a new user
            user = User.query.filter_by(user_id=user_info["user_id"]).first()
            if not user:
                user = User(
                    email=user_info["email"],
                    user_id=user_info["user_id"],
                    first_name=user_info["given_name"],
                    last_name=user_info["family_name"],
                )
                db.session.add(user)
                db.session.commit()

            # check user role
            user_role = UserRole.query.filter_by(user_id=user.user_id).first()
            if not user_role:
                user_role = UserRole(user_id=user.user_id, role="app_user")  # Default role
                db.session.add(user_role)
                db.session.commit()
            login_user(user)
            flask_session["user_role"] = user_role.role
        except Exception as e:
            current_app.logger.error(f"Error occurred while querying user info: {e}")
            db.session.rollback()
            flask_session["user_role"] = 'app_user' #default to app_user if db query fails
        print("this is user-info!!!!!!!!!:", user_info)

        next_url = flask_session.pop("next_url", request.args.get("state", "/"))
        response = make_response(redirect(next_url))
        # response.set_cookie('logged_in', 'true', max_age=60*60, httponly=False, secure=True)
        return response
    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        db.session.rollback()
        user, user_info, user_role = None, None, None
        flask_session.clear()
        return render_template("login_error.html"), 400


@auth_bp.route("/logout")
def auth_logout():
    # Clear user session and cookies
    next_url = request.args.get("state") or request.referrer or "/"
    flask_session.clear()
    logout_user()
    response = make_response(redirect(next_url))
    return response


@auth_bp.route("/db_test", methods=["GET"])
def db_test():
    try:
        db.session.execute(text("SELECT * FROM backend.test_connection"))
        return jsonify(
            {"env": os.getenv("FLASK_ENV"), "status": "Database connected successfully"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/session-check")
def session_check():
    if "user_id" in flask_session:
        return jsonify(
            {
                "logged_in": True,
                "user_id": flask_session["user_id"],
                "user_role": flask_session["user_role"],
                "email_list": get_email_list() or [],
            }
        ), 200
    else:
        return jsonify({"logged_in": False}), 401


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.user_id == user_id).first()