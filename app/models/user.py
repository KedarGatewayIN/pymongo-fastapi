from pydantic import Field, EmailStr, BaseModel
from beanie import Document

# Updated UserCreate to include password
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str # This will be the plain password provided by the user

# New: Model for user login requests (email and password)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Modified User Beanie Document to store the hashed password
class User(Document):
    name: str
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str # <-- NEW: To store the hashed password

    class Settings:
        name = "users"
