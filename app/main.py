# app/main.py
from fastapi import FastAPI
from app.core.database import lifespan_mongodb # Import the renamed lifespan function
from app.api.v1.endpoints import users # Import your users router

# Initialize FastAPI with the lifespan handler
app = FastAPI(lifespan=lifespan_mongodb) # Use the imported lifespan_mongodb

# Include your API routers
app.include_router(users.router, prefix="/api/v1", tags=["Users"]) # Add a prefix for API versioning

# You can add a root endpoint if you like
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI MongoDB User API (v1)"} 