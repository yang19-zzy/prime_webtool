import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()  # Loads from .env file if present

# prod-dev switch
ENVIRONMENT = os.environ.get("FLASK_ENV", "development")

# SQLAlchemy / DB
# SQLALCHEMY_DATABASE_URI = URL.create("postgresql", username=os.getenv("AURORA_PG_USER"), password=os.getenv("AURORA_PG_PW"), host=os.getenv("AURORA_PG_HOST"), port=os.getenv("AURORA_PG_PORT"), database=os.getenv("AURORA_PG_DB"))
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    os.getenv("AURORA_PG_USER"),
    os.getenv("AURORA_PG_PW"),
    os.getenv("AURORA_PG_HOST"),
    os.getenv("AURORA_PG_PORT"),
    os.getenv("AURORA_PG_DB"),
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "execution_options": {"schema_translate_map": {None: "backend"}}
}
SQLALCHEMY_DATABASE_POOL_SIZE = int(os.environ.get("AURORA_PG_POOL_SIZE", 5))
SQLALCHEMY_DATABASE_POOL_RECYCLE = int(os.environ.get("AURORA_PG_POOL_RECYCLE", 1800))

# Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_TIMEOUT = int(os.environ.get("REDIS_TIMEOUT", 1800))

# Flask session
SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
SESSION_COOKIE_NAME = "session"
PERMANENT_SESSION_LIFETIME = timedelta(
    minutes=int(os.environ.get("SESSION_LIFETIME_MINUTES", 300))
)
SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
SESSION_TYPE = "filesystem"

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_AUTH_URI = os.environ.get("GOOGLE_AUTH_URI")
GOOGLE_AUTH_PROVIDER = os.environ.get("GOOGLE_AUTH_PROVIDER")
GOOGLE_TOKEN_URI = os.environ.get("GOOGLE_TOKEN_URI")
GOOGLE_DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL")
GOOGLE_SCOPES = os.environ.get("GOOGLE_SCOPES", "").split()
GOOGLE_REDIRECT_URI = (
    os.environ.get("GOOGLE_REDIRECT_URI_PROD") if ENVIRONMENT == "production" else os.environ.get("GOOGLE_REDIRECT_URI_DEV")
)

GOOGLE_CLIENT_CONFIG = {
    "web": {
        "client_id": GOOGLE_CLIENT_ID,
        "auth_uri": GOOGLE_AUTH_URI,
        "token_uri": GOOGLE_TOKEN_URI,
        "auth_provider_x509_cert_url": GOOGLE_AUTH_PROVIDER,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uris": GOOGLE_REDIRECT_URI.split(),
    }
}

# AWS
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_REGION")
AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
WHITELIST_SECRET_NAME = os.environ.get("WHITELIST_SECRET_NAME")
