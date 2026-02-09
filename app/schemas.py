"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID4
    email: str
    username: str
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    title: Optional[str] = None
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


# Game schemas
class MoveRequest(BaseModel):
    """Move request schema"""
    move: str = Field(..., description="Move in UCI format (e.g., 'e2e4')")


class MoveResponse(BaseModel):
    """Move response schema"""
    fen: str
    san: str
    uci: str
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool
    is_game_over: bool


class GameCreate(BaseModel):
    """Game creation schema"""
    opponent_id: Optional[UUID4] = None
    time_control: str = Field(..., pattern=r"^\d+\+\d+$")  # e.g., "5+0"
    game_type: str = Field(..., pattern="^(casual|rated)$")


class GameResponse(BaseModel):
    """Game response schema"""
    id: UUID4
    white_player_id: UUID4
    black_player_id: UUID4
    time_control: str
    fen: str
    result: str
    game_type: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rating schemas
class RatingResponse(BaseModel):
    """Rating response schema"""
    time_control: str
    rating: int
    rating_deviation: float
    games_played: int
    wins: int
    losses: int
    draws: int
    
    class Config:
        from_attributes = True


# Puzzle schemas
class PuzzleAttemptRequest(BaseModel):
    """Puzzle attempt schema"""
    moves: list[str] = Field(..., description="Attempted solution moves in UCI format")


class PuzzleResponse(BaseModel):
    """Puzzle response schema"""
    id: UUID4
    fen: str
    rating: int
    themes: list[str]
    
    class Config:
        from_attributes = True


# Tournament schemas
class TournamentCreate(BaseModel):
    """Tournament creation schema"""
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    tournament_type: str = Field(..., pattern="^(swiss|round_robin|knockout)$")
    time_control: str
    rounds: Optional[int] = None
    max_players: int = Field(..., gt=1)
    starts_at: datetime


class TournamentResponse(BaseModel):
    """Tournament response schema"""
    id: UUID4
    name: str
    description: Optional[str]
    tournament_type: str
    time_control: str
    status: str
    max_players: int
    starts_at: datetime
    
    class Config:
        from_attributes = True
