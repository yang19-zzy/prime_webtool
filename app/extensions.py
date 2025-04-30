# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
_google = None
_s3 = None
_s3_bucket = None
_redis_client = None

def set_google(client):
    global _google
    _google = client

def get_google():
    if _google is None:
        raise ValueError("Google client has not been set.")
    return _google

def set_s3(client):
    global _s3
    _s3 = client

def get_s3():
    if _s3 is None:
        raise ValueError("S3 client has not been set.")
    return _s3

def set_s3_bucket(bucket):
    global _s3_bucket
    _s3_bucket = bucket

def get_s3_bucket():
    if _s3_bucket is None:
        raise ValueError("S3 bucket has not been set.")
    return _s3_bucket

def set_redis(client):
    global _redis_client
    _redis_client = client

from flask import current_app

def get_redis():
    redis_client = current_app.extensions.get('redis')
    if redis_client is None:
        raise ValueError("Redis client has not been set.")
    return redis_client