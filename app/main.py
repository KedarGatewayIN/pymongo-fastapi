# app/main.py
from fastapi import FastAPI
from app.core.database import lifespan_mongodb # Import the renamed lifespan function
from app.api.v1.users import users # Import your users router
from app.api.v1.products import products # Import your products router
from app.api.v1.auth import auth # Import your auth router

# Initialize FastAPI with the lifespan handler
app = FastAPI(lifespan=lifespan_mongodb) # Use the imported lifespan_mongodb

# Include your API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
