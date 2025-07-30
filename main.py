from fastapi import FastAPI, HTTPException, Depends
from pymongo import AsyncMongoClient
from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId
import contextlib

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

MONGODB_URL = "mongodb://mongo_user:mongo_password@mongodb:27017/"

mongodb_client: AsyncMongoClient = None
db_instance = None

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global mongodb_client, db_instance
    print("Connecting to MongoDB...")
    try:
        mongodb_client = AsyncMongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        await mongodb_client.admin.command('ping')
        db_instance = mongodb_client["mydatabase"]
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        mongodb_client = None
        raise RuntimeError(f"Could not connect to MongoDB: {e}")

    yield 

    print("Closing MongoDB connection...")
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB connection closed.")

app = FastAPI(lifespan=lifespan)

async def get_users_collection():
    if db_instance is None:
        raise HTTPException(status_code=500, detail="Database connection not established.")
    return db_instance["users"]

def user_helper(user_data: dict) -> dict:
    if "_id" in user_data:
        user_data["_id"] = str(user_data["_id"])
    return user_data

@app.post("/users", response_model=User)
async def create_user(user: UserCreate, users_collection=Depends(get_users_collection)):
    user_dict = user.model_dump()
    result = await users_collection.insert_one(user_dict)
    new_user_doc = await users_collection.find_one({"_id": result.inserted_id})
    if not new_user_doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")
    return User.model_validate(user_helper(new_user_doc))

@app.get("/users", response_model=List[User])
async def get_users(users_collection=Depends(get_users_collection)):
    users_list = []
    async for user_doc in users_collection.find():
        users_list.append(User.model_validate(user_helper(user_doc)))
    return users_list

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, users_collection=Depends(get_users_collection)):
    try:
        object_id = ObjectId(user_id)
    except Exception: 
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user_doc = await users_collection.find_one({"_id": object_id})
    if user_doc:
        return User.model_validate(user_helper(user_doc))
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserCreate, users_collection=Depends(get_users_collection)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    update_result = await users_collection.update_one(
        {"_id": object_id},
        {"$set": user_update.model_dump()} 
    )

    if update_result.modified_count == 0:
        existing_user_doc = await users_collection.find_one({"_id": object_id})
        if not existing_user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        return User.model_validate(user_helper(existing_user_doc))

    updated_user_doc = await users_collection.find_one({"_id": object_id})
    if not updated_user_doc: 
        raise HTTPException(status_code=500, detail="Failed to retrieve updated user")

    return User.model_validate(user_helper(updated_user_doc))

@app.delete("/users/{user_id}")
async def delete_user(user_id: str, users_collection=Depends(get_users_collection)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    delete_result = await users_collection.delete_one({"_id": object_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}