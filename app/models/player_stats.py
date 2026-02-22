"""Player stats model for XP, levels, and streaks"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class PlayerStats(Base):
    """Tracks XP, levels, and win/loss/daily streaks per player"""
    __tablename__ = "player_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # XP & Level
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)

    # Streaks
    current_win_streak = Column(Integer, default=0)
    best_win_streak = Column(Integer, default=0)
    current_loss_streak = Column(Integer, default=0)
    daily_streak = Column(Integer, default=0)
    last_played_date = Column(Date, nullable=True)
    games_today = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", backref="player_stats")

    def __repr__(self):
        return f"<PlayerStats user={self.user_id} level={self.level} xp={self.xp}>"
