from fastapi import FastAPI, HTTPException
from pymongo import AsyncMongoClient
from pydantic import BaseModel
from typing import List
from bson import ObjectId

app = FastAPI()

# Replace with your MongoDB URL
MONGODB_URL = "mongodb://mongo:mongo@localhost:27017/"
client = AsyncMongoClient(MONGODB_URL)
db = client["mydatabase"]
users_collection = db["users"]

class UserCreate(BaseModel):
    name: str
    email: str

class User(BaseModel):
    id: str
    name: str
    email: str

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }

@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    result = await users_collection.insert_one(user.dict())
    new_user = await users_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

@app.get("/users", response_model=List[User])
async def get_users():
    users = []
    async for user in users_collection.find():
        users.append(user_helper(user))
    return users

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserCreate):
    update_result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user.dict()}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await users_collection.find_one({"_id": ObjectId(user_id)})
    return user_helper(updated_user)

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    delete_result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}