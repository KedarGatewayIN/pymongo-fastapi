import contextlib
import os
from pymongo import AsyncMongoClient
from beanie import init_beanie
from app.models.user import User
from app.models.product import Product

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongo_user:mongo_password@localhost:27017/")
db_client: AsyncMongoClient = None
db_instance = None

@contextlib.asynccontextmanager
async def lifespan_mongodb(app):
    global db_client # Only need db_client for Beanie initialization now
    print("Connecting to MongoDB and Initializing Beanie...")
    try:
        db_client = AsyncMongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)

        # Ping to ensure connection is established before Beanie init
        await db_client.admin.command('ping')

        # Initialize Beanie with the client and document models
        await init_beanie(
            database=db_client["mydatabase"], # Your database name
            document_models=[User, Product] # List of Beanie Document models to register
        )
        print("Connected to MongoDB and Beanie initialized successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB or initialize Beanie: {e}")
        db_client = None
        raise RuntimeError(f"Could not connect to MongoDB or initialize Beanie: {e}")

    yield

    print("Closing MongoDB connection...")
    if db_client:
        db_client.close()
        print("MongoDB connection closed.")
