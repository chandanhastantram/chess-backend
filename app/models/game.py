"""Game model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Index, func, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Game(Base):
    """Chess game model"""
    __tablename__ = "games"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Players
    white_player_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    black_player_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Time control
    time_control = Column(String(20))  # e.g., "5+0", "10+5"
    base_time = Column(Integer)  # seconds
    increment = Column(Integer)  # seconds
    
    # Game data
    pgn = Column(Text)
    fen = Column(String(100))
    moves = Column(ARRAY(String))  # Array of UCI moves
    
    # Result
    result = Column(String(10))  # "1-0", "0-1", "1/2-1/2", "*"
    termination = Column(String(50))  # checkmate, resignation, timeout, draw, etc.
    winner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Metadata
    game_type = Column(String(20))  # casual, rated, tournament
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id"), nullable=True)
    opening_name = Column(String(100))
    opening_eco = Column(String(10))
    
    # Timestamps
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    white_player = relationship("User", foreign_keys=[white_player_id], back_populates="games_as_white")
    black_player = relationship("User", foreign_keys=[black_player_id], back_populates="games_as_black")
    winner = relationship("User", foreign_keys=[winner_id])
    tournament = relationship("Tournament", back_populates="games")
    move_history = relationship("Move", back_populates="game", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_game_players', 'white_player_id', 'black_player_id'),
        Index('idx_game_started_at', 'started_at'),
        Index('idx_game_tournament', 'tournament_id'),
    )
    
    def __repr__(self):
        return f"<Game {self.id} {self.result}>"
