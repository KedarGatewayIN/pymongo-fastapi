# app/api/v1/products/products.py
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated
from beanie import PydanticObjectId # Beanie's ObjectId type for path parameters

# Import models
from app.models.product import Product, ProductCreate
from app.models.response_models import ProductWithUser
from app.models.user import User # Import User to validate creator_id

from fastapi.security import OAuth2PasswordBearer
from app.core.security import decode_access_token
from app.core.cache import get_redis_client
import json
import logging

# Define the OAuth2 scheme (remains the same)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
CACHE_TTL_SECONDS = 60
logger = logging.getLogger(__name__)

# Dependency to get the current authenticated user (remains the same)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = await User.find_one(User.email == email)
    if user is None:
        raise credentials_exception
    
    return user

router = APIRouter(dependencies=[Depends(get_current_user)]) # <-- Global dependency for this router!

@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate, current_user: User = Depends(get_current_user)):
    # Optional: Validate if the creator_id actually belongs to an existing user
    creator_exists = await User.find_one(User.id == current_user.id)
    if not creator_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creator with ID {product_in.creator_id} not found."
        )

    new_product = Product(**product_in.model_dump(), creator_id=current_user.id)
    await new_product.insert()
    return new_product

@router.get("/products/withUsers", response_model=List[ProductWithUser])
async def get_products():
    redis_client = get_redis_client()
    cache_key = "all_products"

    cached_products_json = await redis_client.get(cache_key)

    if cached_products_json:
        logger.info("Cache hit for products!")
        return json.loads(cached_products_json)

    logger.info("Cache miss for products. Fetching from database...")

    products = await Product.aggregate([
        {
            "$lookup": {
                "from": "users",  # The collection name for users
                "localField": "creator_id",
                "foreignField": "_id",
                "as": "creator"
            }
        },
        {
            "$unwind": "$creator"  # Unwind the creator field to get a single object
        }
    ], projection_model=ProductWithUser).to_list()
    return products

@router.get("/products", response_model=List[Product])
async def get_products():
    products = await Product.find_all().to_list()
    return products

@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: PydanticObjectId):
    product = await Product.find_one(Product.id == product_id)
    if product:
        return product
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

@router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: PydanticObjectId, product_update: ProductCreate):
    product = await Product.find_one(Product.id == product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Update fields from product_update
    product.name = product_update.name
    product.description = product_update.description
    product.price = product_update.price
    product.category = product_update.category
    # If creator_id is updated, validate it again
    if product.creator_id != product_update.creator_id:
        creator_exists = await User.find_one(User.id == product_update.creator_id)
        if not creator_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"New creator with ID {product_update.creator_id} not found."
            )
        product.creator_id = product_update.creator_id


    await product.save()
    return product

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: PydanticObjectId):
    product = await Product.find_one(Product.id == product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    await product.delete()
    return {"message": "Product deleted"}
