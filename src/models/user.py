from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    phone_number: str
    role: str = "user"
    email: EmailStr = Field(..., description="Unique email address for the user")  # <- required field

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    user_id: str
    username: str
    phone_number: str
    role: str
    created_at: str
    email: EmailStr