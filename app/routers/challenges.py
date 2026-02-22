"""Challenge routes — challenge friends to play"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, UUID4
import uuid

from app.database import get_db
from app.models.user import User
from app.models.game import Game
from app.models.challenge import Challenge, ChallengeStatus
from app.middleware.auth import get_current_user

router = APIRouter()


# Schemas
class ChallengeCreateRequest(BaseModel):
    opponent_id: UUID4
    time_control: str = Field(default="5+0", pattern=r"^\d+\+\d+$")
    game_type: str = Field(default="casual", pattern="^(casual|rated)$")


class ChallengeResponse(BaseModel):
    id: UUID4
    challenger_id: UUID4
    challenger_username: Optional[str] = None
    challenged_id: UUID4
    challenged_username: Optional[str] = None
    time_control: str
    game_type: str
    status: str
    game_id: Optional[UUID4] = None
    created_at: datetime
    expires_at: Optional[datetime] = None


@router.post("", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    request: ChallengeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Challenge a specific user to a chess game"""
    if request.opponent_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot challenge yourself"
        )

    # Check opponent exists
    result = await db.execute(select(User).where(User.id == request.opponent_id))
    opponent = result.scalar_one_or_none()
    if not opponent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opponent not found"
        )

    # Check for existing pending challenge
    existing = await db.execute(
        select(Challenge).where(
            Challenge.challenger_id == current_user.id,
            Challenge.challenged_id == request.opponent_id,
            Challenge.status == ChallengeStatus.PENDING,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending challenge to this player"
        )

    challenge = Challenge(
        challenger_id=current_user.id,
        challenged_id=request.opponent_id,
        time_control=request.time_control,
        game_type=request.game_type,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)

    return {
        "id": challenge.id,
        "challenger_id": current_user.id,
        "challenger_username": current_user.username,
        "challenged_id": request.opponent_id,
        "challenged_username": opponent.username,
        "time_control": challenge.time_control,
        "game_type": challenge.game_type,
        "status": challenge.status.value,
        "game_id": None,
        "created_at": challenge.created_at,
        "expires_at": challenge.expires_at,
    }


@router.get("/pending", response_model=list[ChallengeResponse])
async def get_pending_challenges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all pending challenges received by the current user"""
    # Expire old challenges first
    old_challenges = await db.execute(
        select(Challenge).where(
            Challenge.status == ChallengeStatus.PENDING,
            Challenge.expires_at < datetime.utcnow()
        )
    )
    for c in old_challenges.scalars().all():
        c.status = ChallengeStatus.EXPIRED

    # Get pending challenges
    result = await db.execute(
        select(Challenge).where(
            Challenge.challenged_id == current_user.id,
            Challenge.status == ChallengeStatus.PENDING,
        )
    )
    challenges = result.scalars().all()

    responses = []
    for c in challenges:
        # Get challenger info
        challenger_result = await db.execute(select(User).where(User.id == c.challenger_id))
        challenger = challenger_result.scalar_one_or_none()

        responses.append({
            "id": c.id,
            "challenger_id": c.challenger_id,
            "challenger_username": challenger.username if challenger else "Unknown",
            "challenged_id": c.challenged_id,
            "challenged_username": current_user.username,
            "time_control": c.time_control,
            "game_type": c.game_type,
            "status": c.status.value,
            "game_id": c.game_id,
            "created_at": c.created_at,
            "expires_at": c.expires_at,
        })

    return responses


@router.get("/sent", response_model=list[ChallengeResponse])
async def get_sent_challenges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all challenges sent by the current user"""
    result = await db.execute(
        select(Challenge).where(
            Challenge.challenger_id == current_user.id,
            Challenge.status == ChallengeStatus.PENDING,
        )
    )
    challenges = result.scalars().all()

    responses = []
    for c in challenges:
        challenged_result = await db.execute(select(User).where(User.id == c.challenged_id))
        challenged = challenged_result.scalar_one_or_none()

        responses.append({
            "id": c.id,
            "challenger_id": c.challenger_id,
            "challenger_username": current_user.username,
            "challenged_id": c.challenged_id,
            "challenged_username": challenged.username if challenged else "Unknown",
            "time_control": c.time_control,
            "game_type": c.game_type,
            "status": c.status.value,
            "game_id": c.game_id,
            "created_at": c.created_at,
            "expires_at": c.expires_at,
        })

    return responses


@router.post("/{challenge_id}/accept")
async def accept_challenge(
    challenge_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept a challenge and create a game"""
    result = await db.execute(
        select(Challenge).where(
            Challenge.id == challenge_id,
            Challenge.challenged_id == current_user.id,
            Challenge.status == ChallengeStatus.PENDING,
        )
    )
    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found or already resolved"
        )

    # Check expiration
    if challenge.expires_at and challenge.expires_at < datetime.utcnow():
        challenge.status = ChallengeStatus.EXPIRED
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Challenge has expired"
        )

    # Parse time control
    parts = challenge.time_control.split("+")
    base_time = int(parts[0]) * 60
    increment = int(parts[1])

    # Create the game
    game = Game(
        white_player_id=challenge.challenger_id,
        black_player_id=challenge.challenged_id,
        time_control=challenge.time_control,
        base_time=base_time,
        increment=increment,
        game_type=challenge.game_type,
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        result="*",
    )
    db.add(game)
    await db.flush()

    # Update challenge
    challenge.status = ChallengeStatus.ACCEPTED
    challenge.game_id = game.id

    await db.commit()

    return {
        "message": "Challenge accepted",
        "game_id": str(game.id),
        "time_control": challenge.time_control,
        "game_type": challenge.game_type,
    }


@router.post("/{challenge_id}/decline")
async def decline_challenge(
    challenge_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Decline a challenge"""
    result = await db.execute(
        select(Challenge).where(
            Challenge.id == challenge_id,
            Challenge.challenged_id == current_user.id,
            Challenge.status == ChallengeStatus.PENDING,
        )
    )
    challenge = result.scalar_one_or_none()

    if not challenge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Challenge not found or already resolved"
        )

    challenge.status = ChallengeStatus.DECLINED
    await db.commit()

    return {"message": "Challenge declined"}
