"""Authentication routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from pydantic import BaseModel, Field
from app.database import get_db
from app.models.user import User
from app.models.rating import Rating, TimeControl
from app.schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from app.utils.auth import verify_password, get_password_hash, create_access_token
from app.config import settings
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password
    )
    db.add(user)
    await db.flush()
    
    # Create initial ratings for all time controls
    for time_control in TimeControl:
        rating = Rating(user_id=user.id, time_control=time_control)
        db.add(rating)
    
    await db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user"""
    
    # Get user by email
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
):
    """
    Refresh access token.
    
    Requires a valid (non-expired) token. Returns a new token
    with a fresh expiration time.
    """
    access_token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for the currently authenticated user.
    
    Requires the current password for verification.
    """
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.password_hash = get_password_hash(request.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}
