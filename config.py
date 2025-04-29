# config.py
import os
import toml
from datetime import timedelta

# Optional: Load config.toml if not in production
ENVIRONMENT = os.getenv("FLASK_ENV", "development")
config = toml.load("config.toml") if ENVIRONMENT != "production" else {}

# --- Utility: Nested get with fallback ---
def conf(section, key, fallback=None):
    return os.getenv(
        key.upper(),
        config.get(section, {}).get(key, fallback)
    )

# --- Google OAuth ---
GOOGLE_CLIENT_ID = conf("google", "CLIENT_ID")
GOOGLE_CLIENT_SECRET = conf("google", "CLIENT_SECRET")
GOOGLE_REDIRECT_URI = conf("google", "REDIRECT_URI")
GOOGLE_AUTH_URI = conf("google", "AUTH_URI")
GOOGLE_TOKEN_URI = conf("google", "TOKEN_URI")
GOOGLE_DISCOVERY_URL = conf("google", "DISCOVERY_URL")
GOOGLE_SCOPES = config.get("google", {}).get("SCOPES", [])

# --- AWS ---
AWS_ACCESS_KEY_ID = conf("aws", "ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = conf("aws", "SECRET_ACCESS_KEY")
AWS_REGION = conf("aws", "DEFAULT_REGION")
AWS_BUCKET_NAME = conf("aws", "BUCKET_NAME")
WHITELIST_SECRET_NAME = conf("aws", "WHITELIST_SECRET_NAME")

# --- DB ---
SQLALCHEMY_DATABASE_URI = conf("localhost_db", "URL", "sqlite:///default.db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "execution_options": {"schema_translate_map": {None: "backend"}}
}

# --- Flask session ---
SESSION_TYPE = "filesystem"
SECRET_KEY = os.getenv("SECRET_KEY", "dev")
PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.getenv("SESSION_LIFETIME_MINUTES", "300")))
SESSION_COOKIE_NAME = "session"
SESSION_COOKIE_SECURE = ENVIRONMENT == "production"

# --- Redis ---
REDIS_HOST = conf("redis", "HOST", "localhost")
REDIS_PORT = conf("redis", "PORT", 6379)
REDIS_DB = conf("redis", "DB", 0)
REDIS_TIMEOUT = conf("redis", "TIMEOUT", 1800)