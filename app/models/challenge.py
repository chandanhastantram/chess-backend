"""Challenge model for friend-to-friend game challenges"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.database import Base


class ChallengeStatus(str, enum.Enum):
    """Challenge status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class Challenge(Base):
    """Challenge a specific user to a chess game"""
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenger_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenged_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    time_control = Column(String(20), default="5+0")   # e.g., "5+0", "10+5"
    game_type = Column(String(20), default="casual")     # casual or rated

    status = Column(Enum(ChallengeStatus), default=ChallengeStatus.PENDING)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=True)  # set when accepted

    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    challenger = relationship("User", foreign_keys=[challenger_id])
    challenged = relationship("User", foreign_keys=[challenged_id])
    game = relationship("Game", foreign_keys=[game_id])

    __table_args__ = (
        Index('idx_challenge_challenged', 'challenged_id', 'status'),
        Index('idx_challenge_challenger', 'challenger_id', 'status'),
    )

    def __repr__(self):
        return f"<Challenge {self.challenger_id} -> {self.challenged_id} [{self.status.value}]>"
