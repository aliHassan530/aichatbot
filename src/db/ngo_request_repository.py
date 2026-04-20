# import uuid
# from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
# from typing import Optional, Dict, Any
# from mysql.connector import Error
# from .connection import get_connection


# def ensure_request_table():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS NgoRequests (
#             request_id CHAR(36) PRIMARY KEY,
#             user_id CHAR(36) NOT NULL,
#             purpose VARCHAR(255) NOT NULL,
#             description TEXT,
#             payment DECIMAL(10,2) NULL,
#             created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
#         )
#         """
#     )
#     conn.commit()
#     cursor.close()
#     conn.close()


# def _row_to_request(row) -> Dict[str, Any]:
#     return {
#         "request_id": row[0],
#         "user_id": row[1],
#         "purpose": row[2],
#         "description": row[3],
#         "payment": float(row[4]) if row[4] is not None else None,
#         "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S"),
#     }


# def create_ngo_request(
#     user_id: str,
#     purpose: str,
#     description: Optional[str],
#     payment: Optional[float] = None,
# ) -> Dict[str, Any]:
#     ensure_request_table()
#     request_id = str(uuid.uuid4())
#     payment_value = None
#     if payment is not None:
#         try:
#             payment_value = Decimal(str(payment)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
#         except (InvalidOperation, ValueError):
#             payment_value = None
#     conn = get_connection()
#     cursor = conn.cursor()
#     try:
#         cursor.execute(
#             "INSERT INTO NgoRequests (request_id, user_id, purpose, description, payment) VALUES (%s, %s, %s, %s, %s)",
#             (request_id, user_id, purpose, description, payment_value),
#         )
#         conn.commit()
#         cursor.execute(
#             "SELECT request_id, user_id, purpose, description, payment, created_at FROM NgoRequests WHERE request_id=%s",
#             (request_id,),
#         )
#         row = cursor.fetchone()
#         return _row_to_request(row)
#     except Error as e:
#         raise e
#     finally:
#         cursor.close()
#         conn.close()

