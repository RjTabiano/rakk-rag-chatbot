import mysql.connector
from app.core.config import DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        port=DB_PORT,
        connection_timeout=10
    )