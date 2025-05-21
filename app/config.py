# config.py
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv("instances/.env")

class Config:
    # Oracle DB creds
    DB_USER     = os.getenv("DB_USER", "bluegay")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    DB_HOST     = os.getenv("DB_HOST", "localhost")
    DB_PORT     = os.getenv("DB_PORT", "1521")
    DB_SERVICE  = os.getenv("DB_SERVICE", "orcl")

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = (
        f"oracle+cx_oracle://{DB_USER}:"
        f"{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/"
        f"{DB_SERVICE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # (tuỳ chọn) secret key cho session/forms
    SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret")
