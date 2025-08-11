import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()  # Loads from .env file if present

# prod-dev switch
ENVIRONMENT = os.environ.get("FLASK_ENV", "development")

# SQLAlchemy / DB
# SQLALCHEMY_DATABASE_URI = URL.create("postgresql", username=os.getenv("AWS_RDS_PG_USER"), password=os.getenv("AWS_RDS_PG_PW"), host=os.getenv("AWS_RDS_PG_HOST"), port=os.getenv("AWS_RDS_PG_PORT"), database=os.getenv("AWS_RDS_PG_DB"))
if ENVIRONMENT == "production":
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://{}:{}@{}:{}/{}?sslmode=require".format(
            os.getenv("AWS_RDS_PG_USER"),
            os.getenv("AWS_RDS_PG_PW"),
            os.getenv("AWS_RDS_PG_HOST"),
            os.getenv("AWS_RDS_PG_PORT"),
            os.getenv("AWS_RDS_PG_DB"),
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "execution_options": {"schema_translate_map": {None: "backend"}},
        "pool_pre_ping": os.getenv("AWS_RDS_PG_POOL_PRE_PING", True),
        "pool_recycle": int(os.environ.get("AWS_RDS_PG_POOL_RECYCLE", 1800)),
        "pool_size": int(os.environ.get("AWS_RDS_PG_POOL_SIZE", 5)),
        "pool_timeout": int(os.environ.get("AWS_RDS_PG_POOL_TIMEOUT", 30)),
    }
    SQLALCHEMY_DATABASE_POOL_SIZE = int(os.environ.get("AWS_RDS_PG_POOL_SIZE", 5))
    SQLALCHEMY_DATABASE_POOL_RECYCLE = int(
        os.environ.get("AWS_RDS_PG_POOL_RECYCLE", 1800)
    )
else:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "execution_options": {"schema_translate_map": {None: "backend"}}
    }

# Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_TIMEOUT = int(os.environ.get("REDIS_TIMEOUT", 1800))

# Flask session
# SESSION_COOKIE_NAME = "session"
# SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
SESSION_PERMANET = (
    False  # Set to True if you want sessions to persist across server restarts
)
SESSION_TYPE = "filesystem"
PERMANENT_SESSION_LIFETIME = timedelta(
    minutes=int(os.environ.get("SESSION_LIFETIME_MINUTES", 45))
)
LAB_NAME = os.environ.get("LAB_NAME", "PRIME")

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_AUTH_URI = os.environ.get("GOOGLE_AUTH_URI")
GOOGLE_AUTH_PROVIDER = os.environ.get("GOOGLE_AUTH_PROVIDER")
GOOGLE_TOKEN_URI = os.environ.get("GOOGLE_TOKEN_URI")
GOOGLE_DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL")
GOOGLE_SCOPES = os.environ.get("GOOGLE_SCOPES", "").split()
GOOGLE_REDIRECT_URI = (
    os.environ.get("GOOGLE_REDIRECT_URI_PROD")
    if ENVIRONMENT == "production"
    else os.environ.get("GOOGLE_REDIRECT_URI_DEV")
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
# AWS_BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME")
# WHITELIST_SECRET_NAME = os.environ.get("WHITELIST_SECRET_NAME")
AWS_LAMBDA_PDF_EXTRACT = os.environ.get("AWS_LAMBDA_PDF_EXTRACT")
