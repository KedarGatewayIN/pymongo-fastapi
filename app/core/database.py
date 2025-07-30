# app/core/database.py
import contextlib
import os
from pymongo import AsyncMongoClient
from fastapi import HTTPException

# Read MongoDB URL from environment variable
# Provide a default value for local development if the environment variable is not set
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongo_user:mongo_password@localhost:27017/")
db_client: AsyncMongoClient = None
db_instance = None

@contextlib.asynccontextmanager
async def lifespan_mongodb(app):
    global db_client, db_instance
    print("Connecting to MongoDB...")
    try:
        db_client = AsyncMongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        await db_client.admin.command('ping')
        db_instance = db_client["mydatabase"]
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        db_client = None
        raise RuntimeError(f"Could not connect to MongoDB: {e}")

    yield

    print("Closing MongoDB connection...")
    if db_client:
        db_client.close()
        print("MongoDB connection closed.")

async def get_users_collection():
    """Dependency to get the users collection."""
    if db_instance is None:
        raise HTTPException(status_code=500, detail="Database connection not established.")
    return db_instance["users"]