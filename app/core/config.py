import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# JWT Settings
SECRET_KEY: str = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# MongoDB Settings (already defined in core/database.py, but can be centralized here too if preferred)
# MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://mongo_user:mongo_password@localhost:27017/")
# DB_NAME: str = os.getenv("DB_NAME", "mydatabase")