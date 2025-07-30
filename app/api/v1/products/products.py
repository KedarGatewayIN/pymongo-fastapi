# app/api/v1/products/products.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from beanie import PydanticObjectId # Beanie's ObjectId type for path parameters

# Import models
from app.models.product import Product, ProductCreate
from app.models.response_models import ProductWithUser
from app.models.user import User # Import User to validate creator_id

router = APIRouter()

@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product_in: ProductCreate):
    # Optional: Validate if the creator_id actually belongs to an existing user
    creator_exists = await User.find_one(User.id == product_in.creator_id)
    if not creator_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Creator with ID {product_in.creator_id} not found."
        )

    new_product = Product(**product_in.model_dump())
    await new_product.insert()
    return new_product

@router.get("/products/withUsers", response_model=List[ProductWithUser])
async def get_products():

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
