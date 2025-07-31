from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks 
from fastapi.security import OAuth2PasswordRequestForm # For standard OAuth2 password flow

from app.models.user import User, UserCreate, UserLogin # Import updated user models
from app.models.token import Token # Import Token model for response
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.mailer import send_welcome_email

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, background_tasks: BackgroundTasks):
    # Check if a user with this email already exists
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    # Hash the plain password
    hashed_password = get_password_hash(user_in.password)

    # Create a new User document with the hashed password
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password
    )

    await new_user.insert() # Save to MongoDB
    background_tasks.add_task(send_welcome_email, new_user.email, new_user.name)
    return new_user # Returns the user object (FastAPI/Pydantic will filter out hashed_password unless specified)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm provides username (email in our case) and password
    user = await User.find_one(User.email == form_data.username) # 'username' field in form is email

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If authentication successful, create an access token
    access_token = create_access_token(data={"sub": user.email}) # 'sub' is standard for subject
    return {"access_token": access_token, "token_type": "bearer"}