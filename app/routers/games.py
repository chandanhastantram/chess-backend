"""Game management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime
import uuid

from app.database import get_db
from app.models.user import User
from app.models.game import Game
from app.models.rating import Rating, TimeControl
from app.middleware.auth import get_current_user
from app.services.rating_system import RatingSystem
from app.services.chess_engine import ChessEngine
from app.websockets.game_state import game_manager
from pydantic import BaseModel, Field, UUID4

router = APIRouter()


# Schemas
class GameCreateRequest(BaseModel):
    opponent_id: Optional[UUID4] = None
    time_control: str = Field(default="5+0", pattern=r"^\d+\+\d+$")
    game_type: str = Field(default="rated", pattern="^(casual|rated)$")


class GameResponse(BaseModel):
    id: UUID4
    white_player_id: UUID4
    black_player_id: UUID4
    time_control: str
    game_type: str
    fen: str
    result: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MoveRequest(BaseModel):
    move: str = Field(..., description="Move in UCI format")


def parse_time_control(tc: str) -> tuple:
    """Parse time control string like '5+0' into (base_seconds, increment_seconds)"""
    parts = tc.split("+")
    return int(parts[0]) * 60, int(parts[1])


def get_time_control_category(base_minutes: int) -> TimeControl:
    """Determine rating category from base time"""
    if base_minutes < 3:
        return TimeControl.BULLET
    elif base_minutes < 10:
        return TimeControl.BLITZ
    elif base_minutes < 30:
        return TimeControl.RAPID
    else:
        return TimeControl.CLASSICAL


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    request: GameCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new game against a specific opponent"""
    if not request.opponent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="opponent_id is required for direct game creation"
        )
    
    # Get opponent
    result = await db.execute(select(User).where(User.id == request.opponent_id))
    opponent = result.scalar_one_or_none()
    
    if not opponent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opponent not found"
        )
    
    if opponent.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot play against yourself"
        )
    
    # Parse time control
    base_time, increment = parse_time_control(request.time_control)
    
    # Randomly assign colors
    import random
    if random.random() < 0.5:
        white_player_id = current_user.id
        black_player_id = opponent.id
    else:
        white_player_id = opponent.id
        black_player_id = current_user.id
    
    # Create game record
    game = Game(
        white_player_id=white_player_id,
        black_player_id=black_player_id,
        time_control=request.time_control,
        base_time=base_time,
        increment=increment,
        game_type=request.game_type,
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        result="*",
        moves=[],
    )
    
    db.add(game)
    await db.commit()
    await db.refresh(game)
    
    # Create in-memory game state
    game_manager.create_game(
        game_id=str(game.id),
        white_player_id=str(white_player_id),
        black_player_id=str(black_player_id),
        base_time=base_time,
        increment=increment,
    )
    
    return game


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: UUID4,
    db: AsyncSession = Depends(get_db)
):
    """Get game details"""
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    return game


@router.get("/{game_id}/pgn")
async def get_game_pgn(
    game_id: UUID4,
    db: AsyncSession = Depends(get_db)
):
    """Export game in PGN format"""
    result = await db.execute(
        select(Game)
        .where(Game.id == game_id)
        .options(selectinload(Game.white_player), selectinload(Game.black_player))
    )
    game = result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Generate PGN
    engine = ChessEngine()
    for move in (game.moves or []):
        try:
            engine.make_move(move)
        except ValueError:
            break
    
    pgn = engine.get_pgn(
        white_player=game.white_player.username if game.white_player else "White",
        black_player=game.black_player.username if game.black_player else "Black",
        result=game.result or "*"
    )
    
    return {"pgn": pgn}


@router.get("")
async def list_user_games(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's game history"""
    result = await db.execute(
        select(Game)
        .where(or_(
            Game.white_player_id == current_user.id,
            Game.black_player_id == current_user.id
        ))
        .order_by(Game.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    games = result.scalars().all()
    
    return {"games": games, "count": len(games)}


@router.get("/live")
async def list_live_games():
    """List currently active games"""
    active_games = []
    for game_id, game_state in game_manager.games.items():
        if game_state.is_active:
            active_games.append({
                "game_id": game_id,
                "white_player_id": game_state.white_player_id,
                "black_player_id": game_state.black_player_id,
                "fen": game_state.engine.get_fen(),
                "turn": game_state.turn,
                "move_count": len(game_state.moves),
            })
    
    return {"games": active_games, "count": len(active_games)}


@router.post("/{game_id}/complete")
async def complete_game(
    game_id: UUID4,
    result: str,
    termination: str,
    winner_id: Optional[UUID4] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete a game and update ratings
    (Internal endpoint, usually called by WebSocket handlers)
    """
    # Get the game
    game_result = await db.execute(select(Game).where(Game.id == game_id))
    game = game_result.scalar_one_or_none()
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if game.result != "*":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game already completed"
        )
    
    # Update game record
    game.result = result
    game.termination = termination
    game.winner_id = winner_id
    game.ended_at = datetime.utcnow()
    
    # Get in-memory game state for moves and PGN
    game_state = game_manager.get_game(str(game_id))
    if game_state:
        game.moves = game_state.moves
        game.pgn = game_state.engine.get_pgn(result=result)
        
        # Detect opening
        opening = game_state.engine.detect_opening(game_state.moves)
        if opening:
            game.opening_name = opening["name"]
            game.opening_eco = opening["eco"]
    
    # Update ratings if rated game
    if game.game_type == "rated":
        base_minutes = game.base_time // 60
        tc_category = get_time_control_category(base_minutes)
        
        # Get player ratings
        white_rating_result = await db.execute(
            select(Rating).where(
                Rating.user_id == game.white_player_id,
                Rating.time_control == tc_category
            )
        )
        white_rating = white_rating_result.scalar_one_or_none()
        
        black_rating_result = await db.execute(
            select(Rating).where(
                Rating.user_id == game.black_player_id,
                Rating.time_control == tc_category
            )
        )
        black_rating = black_rating_result.scalar_one_or_none()
        
        if white_rating and black_rating:
            # Calculate new ratings
            game_result_value = 0.5  # Draw
            if result == "1-0":
                game_result_value = 1.0
            elif result == "0-1":
                game_result_value = 0.0
            
            new_white, new_black = RatingSystem.calculate_new_ratings(
                white_rating.rating, white_rating.rating_deviation, white_rating.volatility,
                black_rating.rating, black_rating.rating_deviation, black_rating.volatility,
                game_result_value
            )
            
            # Update ratings
            white_rating.rating = new_white["rating"]
            white_rating.rating_deviation = new_white["rating_deviation"]
            white_rating.volatility = new_white["volatility"]
            white_rating.games_played += 1
            
            black_rating.rating = new_black["rating"]
            black_rating.rating_deviation = new_black["rating_deviation"]
            black_rating.volatility = new_black["volatility"]
            black_rating.games_played += 1
            
            # Update win/loss/draw counts
            if result == "1-0":
                white_rating.wins += 1
                black_rating.losses += 1
            elif result == "0-1":
                white_rating.losses += 1
                black_rating.wins += 1
            else:
                white_rating.draws += 1
                black_rating.draws += 1
    
    await db.commit()
    
    # Remove from in-memory storage
    game_manager.remove_game(str(game_id))
    
    return {"success": True, "result": result}
