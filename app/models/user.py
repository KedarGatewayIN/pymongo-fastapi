# app/models/user.py
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional

# Pydantic models
class UserCreate(BaseModel):
    name: str
    email: str

class User(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        extra = 'ignore'

# Helper function to convert MongoDB's _id to string for Pydantic validation
# This can be here or in core/database, keeping it with models for now as it's a model-related transformation
def user_helper(user_data: dict) -> dict:
    if "_id" in user_data:
        user_data["_id"] = str(user_data["_id"])
    return user_data