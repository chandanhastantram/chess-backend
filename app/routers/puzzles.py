"""Puzzle routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, UUID4

from app.database import get_db
from app.models.user import User
from app.models.puzzle import Puzzle, PuzzleAttempt
from app.middleware.auth import get_current_user
from app.services.chess_engine import ChessEngine

router = APIRouter()


# Schemas
class PuzzleResponse(BaseModel):
    id: UUID4
    fen: str
    rating: int
    themes: list[str]
    
    class Config:
        from_attributes = True


class PuzzleAttemptRequest(BaseModel):
    moves: list[str]  # Attempted solution moves in UCI format


class PuzzleAttemptResponse(BaseModel):
    solved: bool
    correct_moves: list[str]
    rating_change: Optional[int] = None


@router.get("/daily", response_model=PuzzleResponse)
async def get_daily_puzzle(
    db: AsyncSession = Depends(get_db)
):
    """Get today's daily puzzle"""
    # Use today's date as seed for consistent daily puzzle
    today = date.today()
    seed = int(today.strftime("%Y%m%d"))
    
    # Get a puzzle based on the day
    result = await db.execute(
        select(Puzzle)
        .order_by(Puzzle.id)
        .offset(seed % 1000)  # Simple deterministic selection
        .limit(1)
    )
    puzzle = result.scalar_one_or_none()
    
    if not puzzle:
        # Fallback to first puzzle
        result = await db.execute(select(Puzzle).limit(1))
        puzzle = result.scalar_one_or_none()
    
    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No puzzles available"
        )
    
    return puzzle


@router.get("/random", response_model=PuzzleResponse)
async def get_random_puzzle(
    min_rating: int = 800,
    max_rating: int = 2500,
    theme: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get a random puzzle within rating range"""
    query = select(Puzzle).where(
        Puzzle.rating >= min_rating,
        Puzzle.rating <= max_rating
    )
    
    if theme:
        query = query.where(Puzzle.themes.contains([theme]))
    
    query = query.order_by(func.random()).limit(1)
    
    result = await db.execute(query)
    puzzle = result.scalar_one_or_none()
    
    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No puzzles match the criteria"
        )
    
    return puzzle


@router.get("/{puzzle_id}", response_model=PuzzleResponse)
async def get_puzzle(
    puzzle_id: UUID4,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific puzzle"""
    result = await db.execute(select(Puzzle).where(Puzzle.id == puzzle_id))
    puzzle = result.scalar_one_or_none()
    
    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puzzle not found"
        )
    
    return puzzle


@router.post("/{puzzle_id}/attempt", response_model=PuzzleAttemptResponse)
async def attempt_puzzle(
    puzzle_id: UUID4,
    request: PuzzleAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit a puzzle solution attempt"""
    # Get puzzle
    result = await db.execute(select(Puzzle).where(Puzzle.id == puzzle_id))
    puzzle = result.scalar_one_or_none()
    
    if not puzzle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puzzle not found"
        )
    
    # Verify moves
    correct_moves = puzzle.moves
    submitted_moves = request.moves
    
    # Check if the solution is correct
    solved = len(submitted_moves) >= len(correct_moves)
    for i, correct_move in enumerate(correct_moves):
        if i >= len(submitted_moves):
            solved = False
            break
        if submitted_moves[i] != correct_move:
            solved = False
            break
    
    # Record the attempt
    attempt = PuzzleAttempt(
        user_id=current_user.id,
        puzzle_id=puzzle_id,
        solved=solved,
        time_taken=0,  # Could be passed from client
    )
    db.add(attempt)
    
    # Update puzzle statistics
    puzzle.attempts += 1
    if solved:
        puzzle.success_rate = (puzzle.success_rate * (puzzle.attempts - 1) + 1) / puzzle.attempts
    else:
        puzzle.success_rate = puzzle.success_rate * (puzzle.attempts - 1) / puzzle.attempts
    
    await db.commit()
    
    return {
        "solved": solved,
        "correct_moves": correct_moves,
        "rating_change": 10 if solved else -5,  # Simplified rating change
    }


@router.get("/stats")
async def get_puzzle_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's puzzle statistics"""
    # Count attempts
    total_result = await db.execute(
        select(func.count(PuzzleAttempt.id))
        .where(PuzzleAttempt.user_id == current_user.id)
    )
    total_attempts = total_result.scalar() or 0
    
    # Count solved
    solved_result = await db.execute(
        select(func.count(PuzzleAttempt.id))
        .where(
            PuzzleAttempt.user_id == current_user.id,
            PuzzleAttempt.solved == True
        )
    )
    solved_count = solved_result.scalar() or 0
    
    return {
        "total_attempts": total_attempts,
        "solved": solved_count,
        "success_rate": solved_count / total_attempts if total_attempts > 0 else 0,
    }
