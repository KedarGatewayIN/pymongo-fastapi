# app/main.py
from fastapi import FastAPI
from app.core.database import lifespan_mongodb # Import the renamed lifespan function
from app.api.v1.users import users # Import your users router
from app.api.v1.products import products # Import your products router
from app.api.v1.auth import auth # Import your auth router
from contextlib import asynccontextmanager
from app.core.cache import connect_to_redis, close_redis_connection # <-- NEW IMPORTS

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with lifespan_mongodb(app):
        await connect_to_redis()
        try:
            yield
        finally:
            await close_redis_connection()

# Initialize FastAPI with the lifespan handler
app = FastAPI(lifespan=lifespan)

# Include your API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
