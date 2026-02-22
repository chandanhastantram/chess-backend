"""Puzzle models"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Puzzle(Base):
    """Chess puzzle model"""
    __tablename__ = "puzzles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Puzzle data
    fen = Column(String(100), nullable=False)  # Starting position
    moves = Column(JSON, nullable=False)  # Solution moves in UCI format
    
    # Difficulty
    rating = Column(Integer, default=1500)
    
    # Themes/tags
    themes = Column(JSON)  # e.g., ["fork", "pin", "skewer"]
    
    # Statistics
    popularity = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    puzzle_attempts = relationship("PuzzleAttempt", back_populates="puzzle")
    
    # Indexes
    __table_args__ = (
        Index('idx_puzzle_rating', 'rating'),
    )
    
    def __repr__(self):
        return f"<Puzzle {self.id} rating:{self.rating}>"


class PuzzleAttempt(Base):
    """User puzzle attempt tracking"""
    __tablename__ = "puzzle_attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    puzzle_id = Column(UUID(as_uuid=True), ForeignKey("puzzles.id", ondelete="CASCADE"), nullable=False)
    
    solved = Column(Boolean, nullable=False)
    time_taken = Column(Integer)  # seconds
    attempted_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="puzzle_attempts")
    puzzle = relationship("Puzzle", back_populates="puzzle_attempts")
    
    # Indexes
    __table_args__ = (
        Index('idx_puzzle_attempt_user', 'user_id', 'attempted_at'),
    )
    
    def __repr__(self):
        return f"<PuzzleAttempt user:{self.user_id} solved:{self.solved}>"
