"""Rating model for Glicko-2 rating system"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base


class TimeControl(str, enum.Enum):
    """Time control categories"""
    BULLET = "bullet"
    BLITZ = "blitz"
    RAPID = "rapid"
    CLASSICAL = "classical"


class Rating(Base):
    """Player ratings per time control using Glicko-2 system"""
    __tablename__ = "ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    time_control = Column(Enum(TimeControl), nullable=False)
    
    # Glicko-2 parameters
    rating = Column(Integer, default=1500)
    rating_deviation = Column(Float, default=350.0)
    volatility = Column(Float, default=0.06)
    
    # Statistics
    games_played = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'time_control', name='uq_user_time_control'),
        Index('idx_rating_time_control', 'time_control', 'rating'),
    )
    
    def __repr__(self):
        return f"<Rating {self.user_id} {self.time_control.value}: {self.rating}>"
