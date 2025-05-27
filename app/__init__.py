# app/__init__.py

from flask import Flask
from config import *
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

from app.models import *
from app.utils.s3_fetcher import connect_s3
from authlib.integrations.flask_client import OAuth

from app.extensions import db, oauth, set_google, get_google, set_google_flow, set_s3, set_s3_bucket, migrate
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.blueprints.main import main_bp
from app.blueprints.auth import auth_bp
from app.blueprints.tracker import tracker_bp
from app.blueprints.viewer import viewer_bp
from app.blueprints.validator import validator_bp

from redis import Redis

from app.dash_viewer.init_dash import init_dash as init_dash_viewer


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object('config')
    
    #add LAB_NAME
    @app.context_processor
    def inject_lab_name():
        return dict(lab_name=app.config.get('LAB_NAME', 'PRIME'))

    CORS(app, supports_credentials=True, origins=["http://localhost", "https://prime.kines.umich.edu"])
    
    # Initialize extensions
    ## Google OAuth
    oauth.init_app(app)
    google_client = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={"scope": app.config['GOOGLE_SCOPES']},
    )
    set_google(google_client)

    ## Google 
    flow = InstalledAppFlow.from_client_config(
        client_config = app.config['GOOGLE_CLIENT_CONFIG'],
        scopes = app.config['GOOGLE_SCOPES'],
        redirect_uri = app.config['GOOGLE_REDIRECT_URI']
    )
    set_google_flow(flow)
    
    ## S3 connection
    s3_client = connect_s3(
        key=app.config['AWS_ACCESS_KEY_ID'],
        secret=app.config['AWS_SECRET_ACCESS_KEY'],
        region=app.config['AWS_REGION']
    )
    set_s3(s3_client)

    ## S3 bucket name - this is used in blueprints
    s3_bucket_ = app.config['AWS_BUCKET_NAME']
    set_s3_bucket(s3_bucket_)

    # Initialize Dash app
    init_dash_viewer(app)
    
    # Initialize database
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize Redis
    redis_client = Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        decode_responses=True
    )
    try:
        redis_client.ping()
        print("Redis connection successful")
    except Exception as e:
        print(f"Redis connection failed: {e}")
    app.extensions['redis'] = redis_client


    # Initialize ProxyFix middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_port=1, x_proto=1)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(viewer_bp)
    app.register_blueprint(tracker_bp)
    app.register_blueprint(validator_bp)


    print(app.url_map)
    # print("=== FINAL SQLAlchemy DB URI ===")
    # print(app.config['SQLALCHEMY_DATABASE_URI'])
    # print("Google Config", app.config['GOOGLE_CLIENT_CONFIG'])
    return app