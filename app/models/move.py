"""Move model for detailed game analysis"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Move(Base):
    """Individual chess move for analysis"""
    __tablename__ = "moves"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False)
    
    move_number = Column(Integer, nullable=False)
    color = Column(String(5), nullable=False)  # white or black
    
    # Move notation
    san = Column(String(10), nullable=False)  # Standard Algebraic Notation
    uci = Column(String(10), nullable=False)  # Universal Chess Interface
    
    # Board state after move
    fen_after = Column(String(100), nullable=False)
    
    # Time tracking
    time_left = Column(Integer)  # milliseconds remaining
    timestamp = Column(DateTime, server_default=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="move_history")
    
    def __repr__(self):
        return f"<Move {self.move_number}. {self.san}>"
