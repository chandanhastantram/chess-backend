"""User model"""
from sqlalchemy import Column, String, DateTime, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    avatar_url = Column(String(500))
    country = Column(String(3))  # ISO 3166-1 alpha-3
    bio = Column(String(500))
    
    # Preferences
    preferred_board_theme = Column(String(50), default="classic")
    preferred_piece_set = Column(String(50), default="standard")
    title = Column(String(10))  # GM, IM, FM, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    last_seen = Column(DateTime, onupdate=func.now())
    
    # Relationships
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    games_as_white = relationship(
        "Game",
        foreign_keys="Game.white_player_id",
        back_populates="white_player"
    )
    games_as_black = relationship(
        "Game",
        foreign_keys="Game.black_player_id",
        back_populates="black_player"
    )
    puzzle_attempts = relationship("PuzzleAttempt", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"
