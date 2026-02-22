"""Post-game analysis routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel, UUID4

from app.database import get_db
from app.models.user import User
from app.models.game import Game
from app.models.game_analysis import GameAnalysis, MoveAnalysis
from app.middleware.auth import get_current_user
from app.services.analysis_service import AnalysisService

router = APIRouter()


# Schemas
class MoveAnalysisResponse(BaseModel):
    move_number: int
    color: str
    san: str
    uci: str
    classification: str
    eval_before: Optional[float] = None
    eval_after: Optional[float] = None
    best_move_san: Optional[str] = None
    best_move_uci: Optional[str] = None
    is_best_move: bool
    cp_loss: Optional[float] = None


class GameAnalysisResponse(BaseModel):
    game_id: UUID4
    white_accuracy: Optional[float] = None
    black_accuracy: Optional[float] = None
    white_blunders: int = 0
    white_mistakes: int = 0
    white_inaccuracies: int = 0
    black_blunders: int = 0
    black_mistakes: int = 0
    black_inaccuracies: int = 0
    summary: Optional[str] = None
    moves: list[MoveAnalysisResponse] = []


@router.post("/{game_id}/analyze", response_model=GameAnalysisResponse)
async def analyze_game(
    game_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger full Stockfish analysis of a completed game.
    
    Analyzes every move and classifies them as
    brilliant/great/good/inaccuracy/mistake/blunder.
    Returns per-player accuracy scores.
    """
    # Get the game
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )

    if not game.result or game.result == "*":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not yet completed"
        )

    # Check if analysis already exists
    existing = await db.execute(
        select(GameAnalysis).where(GameAnalysis.game_id == game_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Analysis already exists. Use GET to retrieve it."
        )

    # Run analysis
    moves = game.moves or []
    if not moves:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game has no recorded moves"
        )

    service = AnalysisService()
    analysis_result = await service.analyze_game(moves)

    # Generate summary
    summary_parts = []
    if analysis_result["white_accuracy"] and analysis_result["black_accuracy"]:
        summary_parts.append(
            f"White accuracy: {analysis_result['white_accuracy']}%, "
            f"Black accuracy: {analysis_result['black_accuracy']}%"
        )
    if analysis_result["white_blunders"] or analysis_result["black_blunders"]:
        summary_parts.append(
            f"Blunders: White {analysis_result['white_blunders']}, "
            f"Black {analysis_result['black_blunders']}"
        )
    summary = ". ".join(summary_parts) if summary_parts else "Analysis complete"

    # Save analysis
    game_analysis = GameAnalysis(
        game_id=game_id,
        white_accuracy=analysis_result["white_accuracy"],
        black_accuracy=analysis_result["black_accuracy"],
        white_blunders=analysis_result["white_blunders"],
        white_mistakes=analysis_result["white_mistakes"],
        white_inaccuracies=analysis_result["white_inaccuracies"],
        black_blunders=analysis_result["black_blunders"],
        black_mistakes=analysis_result["black_mistakes"],
        black_inaccuracies=analysis_result["black_inaccuracies"],
        summary=summary,
    )
    db.add(game_analysis)
    await db.flush()

    # Save per-move analyses
    for ma in analysis_result["move_analyses"]:
        move_analysis = MoveAnalysis(
            game_analysis_id=game_analysis.id,
            move_number=ma["move_number"],
            color=ma["color"],
            san=ma["san"],
            uci=ma["uci"],
            classification=ma["classification"],
            eval_before=ma["eval_before"],
            eval_after=ma["eval_after"],
            best_move_san=ma.get("best_move_san"),
            best_move_uci=ma.get("best_move_uci"),
            is_best_move=ma["is_best_move"],
        )
        db.add(move_analysis)

    await db.commit()

    return {
        "game_id": game_id,
        "white_accuracy": analysis_result["white_accuracy"],
        "black_accuracy": analysis_result["black_accuracy"],
        "white_blunders": analysis_result["white_blunders"],
        "white_mistakes": analysis_result["white_mistakes"],
        "white_inaccuracies": analysis_result["white_inaccuracies"],
        "black_blunders": analysis_result["black_blunders"],
        "black_mistakes": analysis_result["black_mistakes"],
        "black_inaccuracies": analysis_result["black_inaccuracies"],
        "summary": summary,
        "moves": [
            {
                "move_number": ma["move_number"],
                "color": ma["color"],
                "san": ma["san"],
                "uci": ma["uci"],
                "classification": ma["classification"],
                "eval_before": ma["eval_before"],
                "eval_after": ma["eval_after"],
                "best_move_san": ma.get("best_move_san"),
                "best_move_uci": ma.get("best_move_uci"),
                "is_best_move": ma["is_best_move"],
                "cp_loss": ma.get("cp_loss"),
            }
            for ma in analysis_result["move_analyses"]
        ],
    }


@router.get("/{game_id}/analysis", response_model=GameAnalysisResponse)
async def get_game_analysis(
    game_id: UUID4,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve cached analysis results for a game"""
    result = await db.execute(
        select(GameAnalysis).where(GameAnalysis.game_id == game_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found. Use POST to trigger analysis first."
        )

    # Get move analyses
    moves_result = await db.execute(
        select(MoveAnalysis)
        .where(MoveAnalysis.game_analysis_id == analysis.id)
        .order_by(MoveAnalysis.move_number)
    )
    move_analyses = moves_result.scalars().all()

    return {
        "game_id": game_id,
        "white_accuracy": analysis.white_accuracy,
        "black_accuracy": analysis.black_accuracy,
        "white_blunders": analysis.white_blunders,
        "white_mistakes": analysis.white_mistakes,
        "white_inaccuracies": analysis.white_inaccuracies,
        "black_blunders": analysis.black_blunders,
        "black_mistakes": analysis.black_mistakes,
        "black_inaccuracies": analysis.black_inaccuracies,
        "summary": analysis.summary,
        "moves": [
            {
                "move_number": ma.move_number,
                "color": ma.color,
                "san": ma.san,
                "uci": ma.uci,
                "classification": ma.classification,
                "eval_before": ma.eval_before,
                "eval_after": ma.eval_after,
                "best_move_san": ma.best_move_san,
                "best_move_uci": ma.best_move_uci,
                "is_best_move": ma.is_best_move,
                "cp_loss": None,
            }
            for ma in move_analyses
        ],
    }
