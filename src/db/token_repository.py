import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from mysql.connector import Error
from .connection import get_connection

def ensure_token_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS UserTokens (
            token VARCHAR(255) PRIMARY KEY,
            user_id CHAR(36) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL
        )
        """
    )
    conn.commit()
    cursor.close()
    conn.close()

def create_token(user_id: str, ttl_minutes: int = 120) -> Dict[str, Any]:
    ensure_token_table()
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(minutes=ttl_minutes)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO UserTokens (token, user_id, expires_at) VALUES (%s, %s, %s)",
            (token, user_id, expires.strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        cursor.execute("SELECT token, user_id, created_at, expires_at FROM UserTokens WHERE token=%s", (token,))
        row = cursor.fetchone()
        return {
            "token": row[0],
            "user_id": row[1],
            "created_at": row[2].strftime("%Y-%m-%d %H:%M:%S"),
            "expires_at": row[3].strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Error as e:
        raise e
    finally:
        cursor.close()
        conn.close()

def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT u.user_id, u.username, u.email, u.phone_number, u.role, u.created_at, t.expires_at
        FROM AuthUsers u
        JOIN UserTokens t ON t.user_id = u.user_id
        WHERE t.token=%s
        """,
        (token,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    expires_at = row[6]
    if expires_at <= datetime.utcnow():
        return None
    return {
        "user_id": row[0],
        "username": row[1],
        "email": row[2],
        "phone_number": row[3],
        "role": row[4],
        "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S"),
    }
