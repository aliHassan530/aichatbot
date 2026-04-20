import uuid
import bcrypt
from typing import Optional, Dict, Any
from mysql.connector import Error, IntegrityError
from .connection import get_connection

def ensure_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS AuthUsers (
            user_id CHAR(36) PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARBINARY(60) NOT NULL,
            phone_number VARCHAR(20),
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    cursor.execute("SHOW COLUMNS FROM AuthUsers LIKE 'email'")
    col = cursor.fetchone()
    if not col:
        cursor.execute("ALTER TABLE AuthUsers ADD COLUMN email VARCHAR(255) UNIQUE")
        conn.commit()
    cursor.close()
    conn.close()

def _row_to_user(row) -> Dict[str, Any]:
    return {
        "user_id": row[0],
        "username": row[1],
        "email": row[2],
        "phone_number": row[3],
        "role": row[4],
        "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S"),
    }

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    ensure_user_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, email, password_hash, phone_number, role, created_at FROM AuthUsers WHERE email=%s",
        (email,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return {
        "user_id": row[0],
        "username": row[1],
        "email": row[2],
        "password_hash": row[3],
        "phone_number": row[4],
        "role": row[5],
        "created_at": row[6].strftime("%Y-%m-%d %H:%M:%S"),
    }

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    ensure_user_table()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, email, password_hash, phone_number, role, created_at FROM AuthUsers WHERE username=%s",
        (username,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return {
        "user_id": row[0],
        "username": row[1],
        "email": row[2],
        "password_hash": row[3],
        "phone_number": row[4],
        "role": row[5],
        "created_at": row[6].strftime("%Y-%m-%d %H:%M:%S"),
    }

def create_user(username: str, email: str, password: str, phone_number: Optional[str], role: str) -> Dict[str, Any]:
    ensure_user_table()
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO AuthUsers (user_id, username, email, password_hash, phone_number, role) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, username, email, password_hash, phone_number, role),
        )
        conn.commit()
        cursor.execute(
            "SELECT user_id, username, email, phone_number, role, created_at FROM AuthUsers WHERE user_id=%s",
            (user_id,),
        )
        row = cursor.fetchone()
        return _row_to_user(row)
    except IntegrityError as e:
        raise e
    except Error as e:
        raise e
    finally:
        cursor.close()
        conn.close()

def verify_password(username: str, password: str) -> bool:
    user = get_user_by_username(username)
    if not user:
        return False
    stored = user["password_hash"]
    return bcrypt.checkpw(password.encode("utf-8"), stored)

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, username, email, phone_number, role, created_at FROM AuthUsers WHERE user_id=%s",
        (user_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return _row_to_user(row)
