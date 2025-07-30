# app/main.py
from fastapi import FastAPI
from app.core.database import lifespan_mongodb # Import the renamed lifespan function
from app.api.v1.users import users # Import your users router
from app.api.v1.products import products # Import your products router

# Initialize FastAPI with the lifespan handler
app = FastAPI(lifespan=lifespan_mongodb) # Use the imported lifespan_mongodb

# Include your API routers
app.include_router(users.router, prefix="/api/v1") # Add a prefix for API versioning
app.include_router(products.router, prefix="/api/v1", tags=["Products"]) # <-- NEW: Include products router

# You can add a root endpoint if you like
@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI MongoDB User API (v1)"} 