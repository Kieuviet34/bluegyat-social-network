# config.py
import os
from dotenv import load_dotenv
load_dotenv()

DB_USER     = os.getenv("DB_USER", "scnw")
DB_PASSWORD = os.getenv("DB_PASSWORD", "sc1234")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "1521")
DB_SERVICE  = os.getenv("DB_SERVICE", "orcl")
