import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# JWT Settings
SECRET_KEY: str = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0") # Default for local dev without Docker

SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", 1025))
SENDER_EMAIL: str = os.getenv("SENDER_EMAIL", "noreply@example.com")
