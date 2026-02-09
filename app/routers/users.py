"""User routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from typing import Optional
from pydantic import BaseModel, UUID4

from app.database import get_db
from app.models.user import User
from app.models.rating import Rating, TimeControl
from app.models.game import Game
from app.models.friendship import Friendship, FriendshipStatus
from app.middleware.auth import get_current_user, get_optional_current_user

router = APIRouter()


# Schemas
class UserProfileResponse(BaseModel):
    id: UUID4
    username: str
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    title: Optional[str] = None
    is_verified: bool
    
    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None


class RatingResponse(BaseModel):
    time_control: str
    rating: int
    rating_deviation: float
    games_played: int
    wins: int
    losses: int
    draws: int


class UserStatsResponse(BaseModel):
    total_games: int
    total_wins: int
    total_losses: int
    total_draws: int
    ratings: list[RatingResponse]


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile"""
    if request.avatar_url is not None:
        current_user.avatar_url = request.avatar_url
    if request.country is not None:
        current_user.country = request.country
    if request.bio is not None:
        current_user.bio = request.bio
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID4,
    db: AsyncSession = Depends(get_db)
):
    """Get a user's profile by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: UUID4,
    db: AsyncSession = Depends(get_db)
):
    """Get a user's game statistics"""
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get ratings
    ratings_result = await db.execute(
        select(Rating).where(Rating.user_id == user_id)
    )
    ratings = ratings_result.scalars().all()
    
    # Calculate totals
    total_games = sum(r.games_played for r in ratings)
    total_wins = sum(r.wins for r in ratings)
    total_losses = sum(r.losses for r in ratings)
    total_draws = sum(r.draws for r in ratings)
    
    return {
        "total_games": total_games,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "total_draws": total_draws,
        "ratings": [
            {
                "time_control": r.time_control.value,
                "rating": r.rating,
                "rating_deviation": r.rating_deviation,
                "games_played": r.games_played,
                "wins": r.wins,
                "losses": r.losses,
                "draws": r.draws,
            }
            for r in ratings
        ]
    }


@router.get("/{user_id}/games")
async def get_user_games(
    user_id: UUID4,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Get a user's game history"""
    result = await db.execute(
        select(Game)
        .where(or_(
            Game.white_player_id == user_id,
            Game.black_player_id == user_id
        ))
        .order_by(Game.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    games = result.scalars().all()
    
    return {"games": games, "count": len(games)}


@router.get("/search")
async def search_users(
    q: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Search users by username"""
    if len(q) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters"
        )
    
    result = await db.execute(
        select(User)
        .where(User.username.ilike(f"%{q}%"))
        .limit(limit)
    )
    users = result.scalars().all()
    
    return {"users": users, "count": len(users)}


# Friend endpoints
@router.post("/{user_id}/friends")
async def send_friend_request(
    user_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a friend request"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send friend request to yourself"
        )
    
    # Check if target user exists
    result = await db.execute(select(User).where(User.id == user_id))
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if friendship already exists
    result = await db.execute(
        select(Friendship).where(
            or_(
                (Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id),
                (Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id)
            )
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friendship already exists or pending"
        )
    
    # Create friend request
    friendship = Friendship(
        user_id=current_user.id,
        friend_id=user_id,
        status=FriendshipStatus.PENDING
    )
    db.add(friendship)
    await db.commit()
    
    return {"message": "Friend request sent"}


@router.post("/{user_id}/friends/accept")
async def accept_friend_request(
    user_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a friend request"""
    result = await db.execute(
        select(Friendship).where(
            Friendship.user_id == user_id,
            Friendship.friend_id == current_user.id,
            Friendship.status == FriendshipStatus.PENDING
        )
    )
    friendship = result.scalar_one_or_none()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )
    
    friendship.status = FriendshipStatus.ACCEPTED
    await db.commit()
    
    return {"message": "Friend request accepted"}


@router.delete("/{user_id}/friends")
async def remove_friend(
    user_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a friend"""
    result = await db.execute(
        select(Friendship).where(
            or_(
                (Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id),
                (Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id)
            )
        )
    )
    friendship = result.scalar_one_or_none()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
    
    await db.delete(friendship)
    await db.commit()
    
    return {"message": "Friend removed"}


@router.get("/me/friends")
async def get_friends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's friends"""
    result = await db.execute(
        select(Friendship).where(
            or_(
                Friendship.user_id == current_user.id,
                Friendship.friend_id == current_user.id
            ),
            Friendship.status == FriendshipStatus.ACCEPTED
        )
    )
    friendships = result.scalars().all()
    
    friends = []
    for f in friendships:
        friend_id = f.friend_id if f.user_id == current_user.id else f.user_id
        result = await db.execute(select(User).where(User.id == friend_id))
        friend = result.scalar_one_or_none()
        if friend:
            friends.append({
                "id": str(friend.id),
                "username": friend.username,
                "avatar_url": friend.avatar_url,
            })
    
    return {"friends": friends, "count": len(friends)}
