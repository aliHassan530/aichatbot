

from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, Field
from typing import Optional
from src.db.token_repository import get_user_by_token
from src.db.ngo_request_repository import create_ngo_request

router = APIRouter()

"""
Simple JSON-only API for creating NGO requests.

How to use (Postman/curl):
1) Get a bearer token via /auth/login
2) Call POST /addNgo/create with:
   - Header: Authorization: Bearer <token>
   - JSON Body:
     {
       "purpose": "School Fee Help",
       "description": "Monthly fee support",
       "payment": 1500.00
     }
"""


class NgoRequestIn(BaseModel):
    # User se lene wali fields (JSON body)
    purpose: str = Field(min_length=3, max_length=255)
    description: Optional[str] = None
    payment: Optional[float] = None


class NgoRequestOut(BaseModel):
    # DB me save hone ke baad jo cheezein wapas bhej rahe hain
    request_id: str
    user_id: str
    purpose: str
    description: Optional[str] = None
    payment: Optional[float] = None
    created_at: str


@router.post("/create", response_model=NgoRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(payload: NgoRequestIn, authorization: str | None = Header(None)):
    # Step 1: Header me "Authorization: Bearer <token>" aana chahiye
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")

    # Step 2: Token se current user nikaalna
    token = authorization.split(" ", 1)[1]
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")

    # Step 3: Payload ko DB me create karna (user_id + purpose + description + payment)
    created = create_ngo_request(
        user_id=user["user_id"],
        purpose=payload.purpose,
        description=payload.description,
        payment=payload.payment,
    )

    # Step 4: JSON response wapas bhejna (201 Created)
    return created
