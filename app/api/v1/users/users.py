# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId

# Import models and database dependency from our new structured paths
from app.models.user import User, UserCreate, user_helper
from app.core.database import get_database_instance

router = APIRouter()

@router.post("/users", response_model=User)
async def create_user(user: UserCreate, db_instance=Depends(get_database_instance)):
    user_dict = user.model_dump()
    result = await db_instance.users.insert_one(user_dict)

    new_user_doc = await db_instance.users.find_one({"_id": result.inserted_id})
    if not new_user_doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve newly created user")

    return User.model_validate(user_helper(new_user_doc))

@router.get("/users", response_model=List[User])
async def get_users(db_instance=Depends(get_database_instance)):
    users_list = []
    async for user_doc in db_instance.users.find():
        users_list.append(User.model_validate(user_helper(user_doc)))
    return users_list

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, db_instance=Depends(get_database_instance)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user_doc = await db_instance.users.find_one({"_id": object_id})
    if user_doc:
        return User.model_validate(user_helper(user_doc))
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserCreate, db_instance=Depends(get_database_instance)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    update_result = await db_instance.users.update_one(
        {"_id": object_id},
        {"$set": user_update.model_dump()}
    )

    if update_result.modified_count == 0:
        existing_user_doc = await db_instance.users.find_one({"_id": object_id})
        if not existing_user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        return User.model_validate(user_helper(existing_user_doc))

    updated_user_doc = await db_instance.users.find_one({"_id": object_id})
    if not updated_user_doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated user")

    return User.model_validate(user_helper(updated_user_doc))

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db_instance=Depends(get_database_instance)):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    delete_result = await db_instance.users.delete_one({"_id": object_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}