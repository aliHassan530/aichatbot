import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME", "TestDB")
    if password is None:
        raise RuntimeError("Missing DB_PASSWORD environment variable")
    return mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        connection_timeout=10,
    )
