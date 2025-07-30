# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId

# Import models and database dependency from our new structured paths
from app.models.user import User, UserCreate, user_helper
from app.core.database import get_users_collection

router = APIRouter()

@router.post("/users", response_model=User)
async def create_user(user: UserCreate, users_collection=Depends(get_users_collection)):
    user_dict = user.model_dump()
    result = await users_collection.insert_one(user_dict)

    new_user_doc = await users_collection.find_one({"_id": result.inserted_id})
    if not new_user_doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")

    return User.model_validate(user_helper(new_user_doc))

@router.get("/users", response_model=List[User])
async def get_users(users_collection=Depends(get_users_collection)):
    users_list = []
    async for user_doc in users_collection.find():
        users_list.append(User.model_validate(user_helper(user_doc)))
    return users_list

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, users_collection=Depends(get_users_collection)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user_doc = await users_collection.find_one({"_id": object_id})
    if user_doc:
        return User.model_validate(user_helper(user_doc))
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserCreate, users_collection=Depends(get_users_collection)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    update_result = await users_collection.update_one(
        {"_id": object_id},
        {"$set": user_update.model_dump()}
    )

    if update_result.modified_count == 0:
        existing_user_doc = await users_collection.find_one({"_id": object_id})
        if not existing_user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        return User.model_validate(user_helper(existing_user_doc))

    updated_user_doc = await users_collection.find_one({"_id": object_id})
    if not updated_user_doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated user")

    return User.model_validate(user_helper(updated_user_doc))

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, users_collection=Depends(get_users_collection)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    delete_result = await users_collection.delete_one({"_id": object_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}