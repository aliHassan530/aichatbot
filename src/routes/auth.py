from fastapi import APIRouter, HTTPException, Header, status
from src.models.user import UserCreate, UserLogin, UserOut
from src.db.user_repository import create_user, verify_password, get_user_by_username, get_user_by_id, get_user_by_email
from src.db.token_repository import create_token, get_user_by_token

router = APIRouter()

@router.get("/hello")
def hello_world():
    return {"message": "Hello from NGO API!"}

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate):
    existing = get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists")
    user = create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        phone_number=payload.phone_number,
        role=payload.role,
    )
    return user

@router.post("/login")
def login(payload: UserLogin):
    ok = verify_password(payload.username, payload.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    user = get_user_by_username(payload.username)
    token_info = create_token(user_id=user["user_id"])
    return {"access_token": token_info["token"], "token_type": "bearer", "expires_at": token_info["expires_at"]}

@router.get("/me", response_model=UserOut)
def me(authorization: str | None = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")
    token = authorization.split(" ", 1)[1]
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    return user
