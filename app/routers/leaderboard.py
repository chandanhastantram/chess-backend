"""Public leaderboard routes"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional
from pydantic import BaseModel, UUID4

from app.database import get_db
from app.models.user import User
from app.models.rating import Rating, TimeControl
from app.models.player_stats import PlayerStats

router = APIRouter()


# Schemas
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID4
    username: str
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    title: Optional[str] = None
    rating: int
    games_played: int
    wins: int
    level: Optional[int] = None
    win_streak: Optional[int] = None


class StreakLeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID4
    username: str
    avatar_url: Optional[str] = None
    current_win_streak: int
    best_win_streak: int
    level: int


class LevelLeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID4
    username: str
    avatar_url: Optional[str] = None
    level: int
    xp: int
    daily_streak: int


@router.get("", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    time_control: str = Query("blitz", pattern="^(bullet|blitz|rapid|classical)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get top players by rating for a specific time control.
    
    Returns ranked list of players sorted by rating descending.
    """
    tc = TimeControl(time_control)

    result = await db.execute(
        select(Rating, User)
        .join(User, Rating.user_id == User.id)
        .where(Rating.time_control == tc)
        .order_by(desc(Rating.rating))
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()

    entries = []
    for i, (rating, user) in enumerate(rows):
        # Get player stats for level/streak info
        stats_result = await db.execute(
            select(PlayerStats).where(PlayerStats.user_id == user.id)
        )
        stats = stats_result.scalar_one_or_none()

        entries.append({
            "rank": offset + i + 1,
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "country": user.country,
            "title": user.title,
            "rating": rating.rating,
            "games_played": rating.games_played,
            "wins": rating.wins,
            "level": stats.level if stats else 1,
            "win_streak": stats.current_win_streak if stats else 0,
        })

    return entries


@router.get("/streaks", response_model=list[StreakLeaderboardEntry])
async def get_streak_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get top players by best win streak"""
    result = await db.execute(
        select(PlayerStats, User)
        .join(User, PlayerStats.user_id == User.id)
        .order_by(desc(PlayerStats.best_win_streak))
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()

    return [
        {
            "rank": offset + i + 1,
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "current_win_streak": stats.current_win_streak,
            "best_win_streak": stats.best_win_streak,
            "level": stats.level,
        }
        for i, (stats, user) in enumerate(rows)
    ]


@router.get("/levels", response_model=list[LevelLeaderboardEntry])
async def get_level_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get top players by level and XP"""
    result = await db.execute(
        select(PlayerStats, User)
        .join(User, PlayerStats.user_id == User.id)
        .order_by(desc(PlayerStats.level), desc(PlayerStats.xp))
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()

    return [
        {
            "rank": offset + i + 1,
            "user_id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url,
            "level": stats.level,
            "xp": stats.xp,
            "daily_streak": stats.daily_streak,
        }
        for i, (stats, user) in enumerate(rows)
    ]
