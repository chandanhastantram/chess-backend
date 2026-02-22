"""Game analysis models for post-game Stockfish review"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class GameAnalysis(Base):
    """Stores overall analysis results for a completed game"""
    __tablename__ = "game_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Accuracy scores (0-100)
    white_accuracy = Column(Float, nullable=True)
    black_accuracy = Column(Float, nullable=True)

    # Summary counts
    white_blunders = Column(Integer, default=0)
    white_mistakes = Column(Integer, default=0)
    white_inaccuracies = Column(Integer, default=0)
    black_blunders = Column(Integer, default=0)
    black_mistakes = Column(Integer, default=0)
    black_inaccuracies = Column(Integer, default=0)

    # Metadata
    summary = Column(String(500), nullable=True)
    analyzed_at = Column(DateTime, server_default=func.now())

    # Relationships
    game = relationship("Game", backref="analysis")
    move_analyses = relationship("MoveAnalysis", back_populates="game_analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<GameAnalysis game={self.game_id} white_acc={self.white_accuracy} black_acc={self.black_accuracy}>"


class MoveAnalysis(Base):
    """Stores per-move Stockfish evaluation for a game"""
    __tablename__ = "move_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_analysis_id = Column(UUID(as_uuid=True), ForeignKey("game_analyses.id", ondelete="CASCADE"), nullable=False)

    move_number = Column(Integer, nullable=False)
    color = Column(String(5), nullable=False)  # "white" or "black"
    san = Column(String(10), nullable=False)   # Standard Algebraic Notation
    uci = Column(String(10), nullable=False)   # UCI notation

    # Classification: brilliant, great, good, inaccuracy, mistake, blunder
    classification = Column(String(20), nullable=False)

    # Evaluation (centipawns, positive = white advantage)
    eval_before = Column(Float, nullable=True)
    eval_after = Column(Float, nullable=True)

    # Best move according to engine
    best_move_san = Column(String(10), nullable=True)
    best_move_uci = Column(String(10), nullable=True)
    is_best_move = Column(Boolean, default=False)

    # Relationships
    game_analysis = relationship("GameAnalysis", back_populates="move_analyses")

    def __repr__(self):
        return f"<MoveAnalysis {self.move_number}. {self.san} [{self.classification}]>"
