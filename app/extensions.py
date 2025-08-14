# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
_google = None
_google_flow = None
_s3 = None
_s3_bucket = None
_s3_metadata = None
_redis_client = None
_email_list = None
# _lambda_client = None


def set_google(client):
    global _google
    _google = client


def get_google():
    if _google is None:
        raise ValueError("Google client has not been set.")
    return _google


def set_google_flow(client):
    global _google_gmail
    _google_gmail = client


def get_google_flow():
    if _google_gmail is None:
        raise ValueError("Google Gmail client has not been set.")
    return _google_gmail


# def set_lambda_client(client):
#     global _lambda_client
#     _lambda_client = client

# def get_lambda_client():
#     if _lambda_client is None:
#         raise ValueError("Lambda client has not been set.")
#     return _lambda_client

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

def set_s3_metadata(metadata):
    global _s3_metadata
    _s3_metadata = metadata

def get_s3_metadata():
    if _s3_metadata is None:
        raise ValueError("S3 metadata has not been set.")
    return _s3_metadata

def set_redis(client):
    global _redis_client
    _redis_client = client

def set_email_list(email_list):
    global _email_list
    _email_list = email_list

def get_email_list():
    if _email_list is None:
        raise ValueError("Email list has not been set.")
    return _email_list

from flask import current_app

def get_redis():
    redis_client = current_app.extensions.get("redis")
    if redis_client is None:
        raise ValueError("Redis client has not been set.")
    return redis_client
