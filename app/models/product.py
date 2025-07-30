# app/models/product.py
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
from typing import Optional

# Pydantic model for creating a product (request body)
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    category: str
    creator_id: str # This will be the ObjectId of the User who created the product

# Beanie Document for the Product collection in MongoDB
class Product(Document):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    creator_id: PydanticObjectId = Field(index=True) # Index this for efficient lookups by creator

    class Settings:
        name = "products" # Collection name in MongoDB
