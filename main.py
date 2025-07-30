from fastapi import FastAPI, HTTPException, Depends
from pymongo import AsyncMongoClient
from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId
import contextlib # Import contextlib for asynccontextmanager

# --- Pydantic Models ---
class UserCreate(BaseModel):
    name: str
    email: str

class User(BaseModel):
    # Use Field with alias to map MongoDB's _id to Pydantic's id
    # The default value `None` and Optional[str] is fine, as _id is set by Mongo
    # But for a response model, we expect it to exist
    id: str = Field(alias="_id")
    name: str
    email: str

    class Config:
        populate_by_name = True # Allows setting 'id' or '_id'
        # This part helps with converting ObjectId to str *when serializing to JSON*
        # It doesn't directly handle the parsing from dict to model via model_validate
        json_encoders = {ObjectId: str}
        # In Pydantic v2, extra='ignore' can be useful to allow additional fields
        # coming from MongoDB without raising errors if they are not in the model.
        # extra='allow' if you want to explicitly allow them
        # extra='forbid' is the default
        extra = 'ignore'

# --- Database Configuration ---
MONGODB_URL = "mongodb://mongo:mongo@localhost:27017/" # Or your actual URL
mongodb_client: AsyncMongoClient = None
db_instance = None

# --- Lifespan Event Handler ---
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global mongodb_client, db_instance
    print("Connecting to MongoDB...")
    try:
        # Use a timeout for connection to prevent indefinite waiting
        mongodb_client = AsyncMongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Attempt to ping the database to ensure connection is established
        await mongodb_client.admin.command('ping')
        db_instance = mongodb_client["mydatabase"]
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        mongodb_client = None
        # Raise the exception to prevent the application from starting if DB connection fails
        raise RuntimeError(f"Could not connect to MongoDB: {e}")

    yield # This yields control to your FastAPI application

    # This code runs after the FastAPI app shuts down
    print("Closing MongoDB connection...")
    if mongodb_client:
        mongodb_client.close()
        print("MongoDB connection closed.")

# Initialize FastAPI with the lifespan handler
app = FastAPI(lifespan=lifespan)

# --- Dependency for MongoDB Collection ---
async def get_users_collection():
    if db_instance is None:
        raise HTTPException(status_code=500, detail="Database connection not established.")
    return db_instance["users"]

# This helper now explicitly converts _id to str before Pydantic validation
# This is often the simplest way to handle _id from MongoDB for model_validate
def user_helper(user_data: dict) -> dict:
    if "_id" in user_data:
        user_data["_id"] = str(user_data["_id"])
    return user_data

# --- API Endpoints ---
@app.post("/users", response_model=User)
async def create_user(user: UserCreate, users_collection=Depends(get_users_collection)):
    # user.model_dump() is correct
    user_dict = user.model_dump()
    result = await users_collection.insert_one(user_dict)
    
    # Retrieve the inserted user to return it, including the generated _id
    new_user_doc = await users_collection.find_one({"_id": result.inserted_id})
    if not new_user_doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")

    # Pass the modified document to model_validate
    return User.model_validate(user_helper(new_user_doc))

@app.get("/users", response_model=List[User])
async def get_users(users_collection=Depends(get_users_collection)):
    users_list = []
    # async for loop for the cursor is correct
    async for user_doc in users_collection.find():
        # Apply the helper to convert _id before validation
        users_list.append(User.model_validate(user_helper(user_doc)))
    return users_list

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, users_collection=Depends(get_users_collection)):
    try:
        object_id = ObjectId(user_id)
    except Exception: # Catching a broader exception for safety, or just InvalidId
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user_doc = await users_collection.find_one({"_id": object_id})
    if user_doc:
        # Apply the helper to convert _id before validation
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
        {"$set": user_update.model_dump()} # Correct for Pydantic v2
    )

    # If nothing was modified, check if user exists. If not, raise 404.
    if update_result.modified_count == 0:
        existing_user_doc = await users_collection.find_one({"_id": object_id})
        if not existing_user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        # If user exists but no changes were made, return the existing user data
        return User.model_validate(user_helper(existing_user_doc))

    updated_user_doc = await users_collection.find_one({"_id": object_id})
    if not updated_user_doc: # This case is less likely if modified_count > 0 but good for robustness
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