"""Offline mode routes — puzzle packs, sync, and opening book"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, UUID4

from app.database import get_db
from app.models.user import User
from app.models.puzzle import Puzzle, PuzzleAttempt
from app.models.game import Game
from app.middleware.auth import get_current_user

router = APIRouter()


# Schemas
class OfflinePuzzle(BaseModel):
    id: UUID4
    fen: str
    moves: list[str]
    rating: int
    themes: list[str]

    class Config:
        from_attributes = True


class OfflinePuzzleAttemptSync(BaseModel):
    puzzle_id: UUID4
    solved: bool
    time_taken: int = 0  # seconds


class OfflineGameSync(BaseModel):
    opponent_name: str
    moves: list[str]
    result: str  # "1-0", "0-1", "1/2-1/2"
    time_control: str
    played_at: Optional[datetime] = None


class OfflineSyncRequest(BaseModel):
    puzzle_attempts: list[OfflinePuzzleAttemptSync] = []
    games: list[OfflineGameSync] = []


class OpeningEntry(BaseModel):
    eco: str
    name: str
    moves: list[str]
    fen_after: str


@router.get("/puzzle-pack", response_model=list[OfflinePuzzle])
async def get_puzzle_pack(
    count: int = 50,
    min_rating: int = 800,
    max_rating: int = 2500,
    db: AsyncSession = Depends(get_db)
):
    """
    Download a batch of puzzles for offline play.
    
    Returns puzzles with their full solutions so they can be 
    attempted without internet connectivity.
    """
    result = await db.execute(
        select(Puzzle)
        .where(
            Puzzle.rating >= min_rating,
            Puzzle.rating <= max_rating
        )
        .order_by(func.random())
        .limit(count)
    )
    puzzles = result.scalars().all()

    return [
        {
            "id": p.id,
            "fen": p.fen,
            "moves": p.moves,
            "rating": p.rating,
            "themes": p.themes,
        }
        for p in puzzles
    ]


@router.post("/sync")
async def sync_offline_data(
    request: OfflineSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync offline results back to the server.
    
    Accepts puzzle attempts and game results completed while offline.
    """
    synced_puzzles = 0
    synced_games = 0

    # Sync puzzle attempts
    for attempt in request.puzzle_attempts:
        puzzle_result = await db.execute(
            select(Puzzle).where(Puzzle.id == attempt.puzzle_id)
        )
        puzzle = puzzle_result.scalar_one_or_none()
        if puzzle:
            db_attempt = PuzzleAttempt(
                user_id=current_user.id,
                puzzle_id=attempt.puzzle_id,
                solved=attempt.solved,
                time_taken=attempt.time_taken,
            )
            db.add(db_attempt)
            puzzle.attempts += 1
            if attempt.solved:
                puzzle.success_rate = (
                    (puzzle.success_rate * (puzzle.attempts - 1) + 1) / puzzle.attempts
                )
            else:
                puzzle.success_rate = (
                    puzzle.success_rate * (puzzle.attempts - 1) / puzzle.attempts
                )
            synced_puzzles += 1

    # Sync offline games (stored as records only, no rating changes)
    for game_data in request.games:
        game = Game(
            white_player_id=current_user.id,
            black_player_id=current_user.id,  # Offline = self-play reference
            time_control=game_data.time_control,
            result=game_data.result,
            game_type="offline",
            moves=game_data.moves,
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            termination="offline",
        )
        db.add(game)
        synced_games += 1

    await db.commit()

    return {
        "message": "Sync completed",
        "synced_puzzles": synced_puzzles,
        "synced_games": synced_games,
    }


@router.get("/opening-book", response_model=list[OpeningEntry])
async def get_opening_book():
    """
    Get common chess openings for offline reference.
    
    Returns a curated set of popular openings with move sequences.
    """
    openings = [
        {
            "eco": "C60",
            "name": "Ruy Lopez",
            "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"],
            "fen_after": "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
        },
        {
            "eco": "B20",
            "name": "Sicilian Defense",
            "moves": ["e2e4", "c7c5"],
            "fen_after": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
        },
        {
            "eco": "D06",
            "name": "Queen's Gambit",
            "moves": ["d2d4", "d7d5", "c2c4"],
            "fen_after": "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3 0 2",
        },
        {
            "eco": "C50",
            "name": "Italian Game",
            "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"],
            "fen_after": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
        },
        {
            "eco": "B01",
            "name": "Scandinavian Defense",
            "moves": ["e2e4", "d7d5"],
            "fen_after": "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2",
        },
        {
            "eco": "C00",
            "name": "French Defense",
            "moves": ["e2e4", "e7e6"],
            "fen_after": "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        },
        {
            "eco": "A45",
            "name": "Indian Defense",
            "moves": ["d2d4", "g8f6"],
            "fen_after": "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 1 2",
        },
        {
            "eco": "B10",
            "name": "Caro-Kann Defense",
            "moves": ["e2e4", "c7c6"],
            "fen_after": "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        },
        {
            "eco": "A00",
            "name": "King's Indian Attack",
            "moves": ["g1f3", "d7d5", "g2g3"],
            "fen_after": "rnbqkbnr/ppp1pppp/8/3p4/8/5NP1/PPPPPP1P/RNBQKB1R b KQkq - 0 2",
        },
        {
            "eco": "D80",
            "name": "Grünfeld Defense",
            "moves": ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "d7d5"],
            "fen_after": "rnbqkb1r/ppp1pp1p/5np1/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq d6 0 4",
        },
        {
            "eco": "E60",
            "name": "King's Indian Defense",
            "moves": ["d2d4", "g8f6", "c2c4", "g7g6"],
            "fen_after": "rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3",
        },
        {
            "eco": "C44",
            "name": "Scotch Game",
            "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "d2d4"],
            "fen_after": "r1bqkbnr/pppp1ppp/2n5/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq d3 0 3",
        },
    ]

    return openings
