"""Post-game analysis service using Stockfish"""
from typing import List, Dict, Optional
from app.services.chess_engine import ChessEngine
from app.services.stockfish_service import StockfishService
import chess


# Move classification thresholds (centipawn loss)
CLASSIFICATION_THRESHOLDS = {
    "brilliant": -200,   # Gains > 2 pawns relative to best (sacrifice/unexpected)
    "great": 0,          # Is the best move
    "good": 30,          # Loses < 0.3 pawns
    "inaccuracy": 100,   # Loses 0.3 - 1.0 pawns
    "mistake": 200,      # Loses 1.0 - 2.0 pawns
    "blunder": 999999,   # Loses > 2.0 pawns
}


class AnalysisService:
    """Analyzes completed games using Stockfish engine"""

    def __init__(self):
        self.stockfish = StockfishService()

    @staticmethod
    def classify_move(cp_loss: float, is_best: bool) -> str:
        """
        Classify a move based on centipawn loss.

        Args:
            cp_loss: Centipawn loss compared to best move (positive = worse)
            is_best: Whether this was the best move

        Returns:
            Classification string
        """
        if is_best:
            return "great"
        if cp_loss <= 0:
            return "brilliant"
        if cp_loss <= 30:
            return "good"
        if cp_loss <= 100:
            return "inaccuracy"
        if cp_loss <= 200:
            return "mistake"
        return "blunder"

    @staticmethod
    def eval_to_centipawns(evaluation: Dict) -> Optional[float]:
        """
        Convert Stockfish evaluation to centipawns.

        Args:
            evaluation: Dict with 'type' and 'value' from Stockfish

        Returns:
            Centipawn value (positive = white advantage)
        """
        if not evaluation:
            return None
        eval_type = evaluation.get("type")
        value = evaluation.get("value")
        if eval_type == "cp":
            return value
        elif eval_type == "mate":
            # Convert mate to large centipawn value
            return 10000 if value > 0 else -10000
        return None

    async def analyze_game(self, moves: List[str], depth: int = 15) -> Dict:
        """
        Analyze all moves in a game.

        Args:
            moves: List of UCI move strings
            depth: Stockfish analysis depth

        Returns:
            Dict with per-move analysis and overall accuracy
        """
        if not moves:
            return {"move_analyses": [], "white_accuracy": 0, "black_accuracy": 0}

        board = chess.Board()
        move_analyses = []
        white_losses = []
        black_losses = []

        prev_eval = 0.0  # Starting position is roughly equal

        for i, move_uci in enumerate(moves):
            move_number = (i // 2) + 1
            color = "white" if i % 2 == 0 else "black"

            fen_before = board.fen()

            # Get the best move for current position
            try:
                analysis = await self.stockfish.analyze_position(fen_before, depth=depth)
                best_move = analysis.get("best_move")
                eval_data = analysis.get("evaluation")
                current_eval = self.eval_to_centipawns(eval_data) or prev_eval
            except Exception:
                best_move = None
                current_eval = prev_eval

            # Make the player's move
            try:
                move = chess.Move.from_uci(move_uci)
                san = board.san(move)
                board.push(move)
            except Exception:
                continue

            # Evaluate position after the move
            try:
                post_analysis = await self.stockfish.analyze_position(board.fen(), depth=depth)
                post_eval_data = post_analysis.get("evaluation")
                post_eval = self.eval_to_centipawns(post_eval_data) or current_eval
            except Exception:
                post_eval = current_eval

            # Calculate centipawn loss
            # For white: loss = best_eval - actual_eval (positive = worse)
            # For black: loss = actual_eval - best_eval (flip perspective)
            if color == "white":
                cp_loss = current_eval - (-post_eval)  # Negate post because it's from black's perspective after move
            else:
                cp_loss = (-current_eval) - post_eval

            # Clamp cp_loss
            cp_loss = max(0, cp_loss)

            is_best = (best_move == move_uci)
            classification = self.classify_move(cp_loss, is_best)

            # Track losses for accuracy
            if color == "white":
                white_losses.append(min(cp_loss, 500))
            else:
                black_losses.append(min(cp_loss, 500))

            # Get best move SAN
            best_move_san = None
            if best_move and best_move != move_uci:
                try:
                    temp_board = chess.Board(fen_before)
                    best_chess_move = chess.Move.from_uci(best_move)
                    best_move_san = temp_board.san(best_chess_move)
                except Exception:
                    best_move_san = best_move

            move_analyses.append({
                "move_number": move_number,
                "color": color,
                "san": san,
                "uci": move_uci,
                "classification": classification,
                "eval_before": round(current_eval / 100, 2),  # In pawns
                "eval_after": round(post_eval / 100, 2),
                "best_move_san": best_move_san,
                "best_move_uci": best_move,
                "is_best_move": is_best,
                "cp_loss": round(cp_loss, 1),
            })

            prev_eval = post_eval

        # Calculate accuracy (chess.com style: 100 - avg_loss)
        white_accuracy = self._calculate_accuracy(white_losses)
        black_accuracy = self._calculate_accuracy(black_losses)

        # Count classifications
        white_counts = {"blunders": 0, "mistakes": 0, "inaccuracies": 0}
        black_counts = {"blunders": 0, "mistakes": 0, "inaccuracies": 0}
        for ma in move_analyses:
            counts = white_counts if ma["color"] == "white" else black_counts
            if ma["classification"] == "blunder":
                counts["blunders"] += 1
            elif ma["classification"] == "mistake":
                counts["mistakes"] += 1
            elif ma["classification"] == "inaccuracy":
                counts["inaccuracies"] += 1

        return {
            "move_analyses": move_analyses,
            "white_accuracy": round(white_accuracy, 1),
            "black_accuracy": round(black_accuracy, 1),
            "white_blunders": white_counts["blunders"],
            "white_mistakes": white_counts["mistakes"],
            "white_inaccuracies": white_counts["inaccuracies"],
            "black_blunders": black_counts["blunders"],
            "black_mistakes": black_counts["mistakes"],
            "black_inaccuracies": black_counts["inaccuracies"],
        }

    @staticmethod
    def _calculate_accuracy(losses: List[float]) -> float:
        """
        Calculate accuracy from centipawn losses (similar to chess.com).
        Formula: accuracy = 103.1668 * exp(-0.04354 * avg_loss) - 3.1668

        Args:
            losses: List of centipawn losses per move

        Returns:
            Accuracy percentage (0-100)
        """
        if not losses:
            return 100.0

        import math
        avg_loss = sum(losses) / len(losses)
        accuracy = 103.1668 * math.exp(-0.04354 * avg_loss) - 3.1668
        return max(0.0, min(100.0, accuracy))
