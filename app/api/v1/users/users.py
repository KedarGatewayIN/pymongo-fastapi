# app/api/v1/endpoints/users.py
from fastapi import APIRouter, HTTPException, status # Import status for clearer HTTP codes
from typing import List
from beanie import PydanticObjectId # Beanie's ObjectId type for path parameters

# Import models
from app.models.user import User, UserCreate

router = APIRouter()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate): # Renamed to avoid conflict with 'User' model
    # Beanie documents are Pydantic models, so user_in is already validated
    # Create a User document from the incoming UserCreate data
    new_user = User(**user_in.model_dump()) # Create a Beanie document instance

    try:
        # Use Beanie's insert() method directly
        await new_user.insert()
    except Exception as e: # Catch potential duplicate key errors (e.g., for unique email)
        if "duplicate key error" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {e}"
        )
    
    # Beanie's insert() automatically populates the _id, so new_user now has it.
    # It also handles the ObjectId -> str conversion for the response_model.
    return new_user

@router.get("/users", response_model=List[User])
async def get_users():
    # Use Beanie's find_all() method to retrieve all documents
    # find_all() returns a Cursor. .to_list() converts it to a list of User objects.
    users = await User.find_all().to_list()
    return users

@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: PydanticObjectId): # Use Beanie's PydanticObjectId for path param
    # Use Beanie's find_one() method by primary key (_id)
    user = await User.find_one(User.id == user_id) # Type-safe query!
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: PydanticObjectId, user_update: UserCreate):
    # Find the user by ID
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update the document using Beanie's set or update methods
    # `set` replaces fields, `update` uses MongoDB operators like $set
    # Beanie allows direct assignment and then saving
    user.name = user_update.name
    user.email = user_update.email

    try:
        await user.save() # Save the updated document
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {e}"
        )

    return user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT) # 204 No Content for successful deletion
async def delete_user(user_id: PydanticObjectId):
    # Find the user by ID
    user = await User.find_one(User.id == user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Delete the document using Beanie's delete() method
    await user.delete()
    return {"message": "User deleted"} # Or simply return None for 204