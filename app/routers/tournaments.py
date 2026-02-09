"""Tournament routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, UUID4

from app.database import get_db
from app.models.user import User
from app.models.rating import Rating, TimeControl
from app.models.tournament import (
    Tournament, TournamentParticipant, TournamentPairing,
    TournamentType, TournamentStatus
)
from app.middleware.auth import get_current_user
from app.services.tournament_service import TournamentService

router = APIRouter()


# Schemas
class TournamentCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    tournament_type: str = Field(..., pattern="^(swiss|round_robin|knockout)$")
    time_control: str = Field(default="5+0", pattern=r"^\d+\+\d+$")
    rounds: Optional[int] = None
    max_players: int = Field(default=16, ge=4, le=256)
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    starts_at: datetime


class TournamentResponse(BaseModel):
    id: UUID4
    name: str
    description: Optional[str]
    tournament_type: str
    time_control: str
    status: str
    max_players: int
    current_round: int
    starts_at: datetime
    participant_count: int = 0
    
    class Config:
        from_attributes = True


class TournamentStandingsResponse(BaseModel):
    rank: int
    user_id: UUID4
    username: str
    score: float
    wins: int
    losses: int
    draws: int


@router.get("", response_model=list[TournamentResponse])
async def list_tournaments(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List tournaments"""
    query = select(Tournament)
    
    if status:
        query = query.where(Tournament.status == TournamentStatus(status))
    
    query = query.order_by(Tournament.starts_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query.options(selectinload(Tournament.participants)))
    tournaments = result.scalars().all()
    
    return [
        {
            **t.__dict__,
            "tournament_type": t.tournament_type.value,
            "status": t.status.value,
            "participant_count": len(t.participants),
        }
        for t in tournaments
    ]


@router.post("", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
async def create_tournament(
    request: TournamentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new tournament"""
    # Parse time control
    parts = request.time_control.split("+")
    base_time = int(parts[0]) * 60
    increment = int(parts[1])
    
    # Determine rounds
    rounds = request.rounds
    if not rounds:
        if request.tournament_type == "swiss":
            # For Swiss, log2(players) + 1
            import math
            rounds = int(math.log2(request.max_players)) + 1
        elif request.tournament_type == "round_robin":
            rounds = request.max_players - 1
    
    tournament = Tournament(
        name=request.name,
        description=request.description,
        tournament_type=TournamentType(request.tournament_type),
        time_control=request.time_control,
        base_time=base_time,
        increment=increment,
        rounds=rounds,
        max_players=request.max_players,
        min_rating=request.min_rating,
        max_rating=request.max_rating,
        status=TournamentStatus.REGISTRATION,
        starts_at=request.starts_at,
    )
    
    db.add(tournament)
    await db.commit()
    await db.refresh(tournament)
    
    return {
        **tournament.__dict__,
        "tournament_type": tournament.tournament_type.value,
        "status": tournament.status.value,
        "participant_count": 0,
    }


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament_id: UUID4,
    db: AsyncSession = Depends(get_db)
):
    """Get tournament details"""
    result = await db.execute(
        select(Tournament)
        .where(Tournament.id == tournament_id)
        .options(selectinload(Tournament.participants))
    )
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    return {
        **tournament.__dict__,
        "tournament_type": tournament.tournament_type.value,
        "status": tournament.status.value,
        "participant_count": len(tournament.participants),
    }


@router.post("/{tournament_id}/join")
async def join_tournament(
    tournament_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Join a tournament"""
    result = await db.execute(
        select(Tournament)
        .where(Tournament.id == tournament_id)
        .options(selectinload(Tournament.participants))
    )
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    if tournament.status != TournamentStatus.REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament is not open for registration"
        )
    
    if len(tournament.participants) >= tournament.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament is full"
        )
    
    # Check if already registered
    for p in tournament.participants:
        if p.user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already registered for this tournament"
            )
    
    # Check rating requirements
    if tournament.min_rating or tournament.max_rating:
        # Get user's relevant rating
        base_minutes = tournament.base_time // 60
        if base_minutes < 3:
            tc = TimeControl.BULLET
        elif base_minutes < 10:
            tc = TimeControl.BLITZ
        elif base_minutes < 30:
            tc = TimeControl.RAPID
        else:
            tc = TimeControl.CLASSICAL
        
        rating_result = await db.execute(
            select(Rating).where(
                Rating.user_id == current_user.id,
                Rating.time_control == tc
            )
        )
        rating = rating_result.scalar_one_or_none()
        user_rating = rating.rating if rating else 1500
        
        if tournament.min_rating and user_rating < tournament.min_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum rating is {tournament.min_rating}"
            )
        
        if tournament.max_rating and user_rating > tournament.max_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum rating is {tournament.max_rating}"
            )
    
    # Add participant
    participant = TournamentParticipant(
        tournament_id=tournament_id,
        user_id=current_user.id,
    )
    db.add(participant)
    await db.commit()
    
    return {"message": "Successfully joined tournament"}


@router.delete("/{tournament_id}/leave")
async def leave_tournament(
    tournament_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave a tournament"""
    result = await db.execute(
        select(TournamentParticipant).where(
            TournamentParticipant.tournament_id == tournament_id,
            TournamentParticipant.user_id == current_user.id
        )
    )
    participant = result.scalar_one_or_none()
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not registered for this tournament"
        )
    
    # Check if tournament has started
    tournament_result = await db.execute(
        select(Tournament).where(Tournament.id == tournament_id)
    )
    tournament = tournament_result.scalar_one_or_none()
    
    if tournament and tournament.status != TournamentStatus.REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave a tournament that has started"
        )
    
    await db.delete(participant)
    await db.commit()
    
    return {"message": "Left tournament"}


@router.get("/{tournament_id}/standings", response_model=list[TournamentStandingsResponse])
async def get_tournament_standings(
    tournament_id: UUID4,
    db: AsyncSession = Depends(get_db)
):
    """Get tournament standings"""
    result = await db.execute(
        select(TournamentParticipant)
        .where(TournamentParticipant.tournament_id == tournament_id)
        .options(selectinload(TournamentParticipant.user))
        .order_by(TournamentParticipant.score.desc())
    )
    participants = result.scalars().all()
    
    standings = []
    for i, p in enumerate(participants):
        standings.append({
            "rank": i + 1,
            "user_id": p.user_id,
            "username": p.user.username if p.user else "Unknown",
            "score": p.score,
            "wins": p.wins,
            "losses": p.losses,
            "draws": p.draws,
        })
    
    return standings


@router.post("/{tournament_id}/start")
async def start_tournament(
    tournament_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a tournament (admin only - for now any registered user)"""
    result = await db.execute(
        select(Tournament)
        .where(Tournament.id == tournament_id)
        .options(selectinload(Tournament.participants))
    )
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    if tournament.status != TournamentStatus.REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tournament is not in registration phase"
        )
    
    if len(tournament.participants) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 2 participants"
        )
    
    # Update status
    tournament.status = TournamentStatus.IN_PROGRESS
    tournament.current_round = 1
    
    # Generate first round pairings
    participant_ids = [str(p.user_id) for p in tournament.participants]
    
    if tournament.tournament_type == TournamentType.ROUND_ROBIN:
        all_pairings = TournamentService.generate_round_robin_pairings(participant_ids)
        round_pairings = all_pairings.get(1, [])
    else:  # Swiss
        participants = [
            {"user_id": str(p.user_id), "score": 0, "rating": 1500, "color_balance": 0}
            for p in tournament.participants
        ]
        round_pairings = TournamentService.generate_swiss_pairings(participants, 1, [])
    
    # Create pairing records
    for white_id, black_id in round_pairings:
        pairing = TournamentPairing(
            tournament_id=tournament_id,
            round_number=1,
            white_player_id=white_id,
            black_player_id=black_id,
        )
        db.add(pairing)
    
    await db.commit()
    
    return {"message": "Tournament started", "round": 1, "pairings": len(round_pairings)}
