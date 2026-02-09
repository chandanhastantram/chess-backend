"""Tournament models"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum, Index, func, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base


class TournamentType(str, enum.Enum):
    """Tournament format types"""
    SWISS = "swiss"
    ROUND_ROBIN = "round_robin"
    KNOCKOUT = "knockout"


class TournamentStatus(str, enum.Enum):
    """Tournament status"""
    UPCOMING = "upcoming"
    REGISTRATION = "registration"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Tournament(Base):
    """Tournament model"""
    __tablename__ = "tournaments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Tournament type
    tournament_type = Column(Enum(TournamentType), nullable=False)
    
    # Settings
    time_control = Column(String(20))
    base_time = Column(Integer)
    increment = Column(Integer)
    rounds = Column(Integer)  # For Swiss
    
    # Capacity
    max_players = Column(Integer)
    min_rating = Column(Integer, nullable=True)
    max_rating = Column(Integer, nullable=True)
    
    # Status
    status = Column(Enum(TournamentStatus), default=TournamentStatus.UPCOMING)
    current_round = Column(Integer, default=0)
    
    # Timestamps
    registration_opens = Column(DateTime)
    registration_closes = Column(DateTime)
    starts_at = Column(DateTime)
    ends_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    participants = relationship("TournamentParticipant", back_populates="tournament", cascade="all, delete-orphan")
    pairings = relationship("TournamentPairing", back_populates="tournament", cascade="all, delete-orphan")
    games = relationship("Game", back_populates="tournament")
    
    def __repr__(self):
        return f"<Tournament {self.name} {self.status.value}>"


class TournamentParticipant(Base):
    """Tournament participant"""
    __tablename__ = "tournament_participants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Tournament stats
    score = Column(Float, default=0.0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    color_balance = Column(Integer, default=0)  # +1 for white, -1 for black
    
    joined_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    tournament = relationship("Tournament", back_populates="participants")
    user = relationship("User")
    
    __table_args__ = (
        Index('idx_tournament_participant', 'tournament_id', 'user_id'),
    )
    
    def __repr__(self):
        return f"<TournamentParticipant tournament:{self.tournament_id} score:{self.score}>"


class TournamentPairing(Base):
    """Swiss/Round-Robin pairings"""
    __tablename__ = "tournament_pairings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(UUID(as_uuid=True), ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    
    white_player_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    black_player_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Null for bye
    
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=True)
    result = Column(String(10), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    tournament = relationship("Tournament", back_populates="pairings")
    white_player = relationship("User", foreign_keys=[white_player_id])
    black_player = relationship("User", foreign_keys=[black_player_id])
    game = relationship("Game")
    
    __table_args__ = (
        Index('idx_tournament_round', 'tournament_id', 'round_number'),
    )
    
    def __repr__(self):
        return f"<TournamentPairing round:{self.round_number}>"
