from pydantic import Field, EmailStr, BaseModel
from beanie import Document # Import Document from beanie

# UserCreate remains a Pydantic BaseModel for request validation
class UserCreate(BaseModel):
    name: str
    email: EmailStr # Using EmailStr for email validation

# User now inherits from beanie.Document
# This is your MongoDB Schema/Model
class User(Document):
    name: str
    email: EmailStr = Field(unique=True, index=True) # Add unique and index for email

    # Optional: Configure the MongoDB collection name
    class Settings:
        name = "users" # This will be the name of your MongoDB collection
