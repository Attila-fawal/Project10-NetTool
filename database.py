import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(override=True)

def get_db_connection():
    db_password = os.getenv("DB_PASSWORD", "")

    # If DB_PASSWORD is blank in .env, connect without a password
    if db_password == "":
        db_password = None

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=db_password,
        database=os.getenv("DB_NAME", "nettool_db")
    )