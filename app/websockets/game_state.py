"""Game state manager for active games"""
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from app.services.chess_engine import ChessEngine


@dataclass
class GameState:
    """Represents the state of an active game"""
    game_id: str
    white_player_id: str
    black_player_id: str
    engine: ChessEngine
    base_time: int  # Base time in seconds
    increment: int  # Increment in seconds
    white_time: int  # Remaining time in milliseconds
    black_time: int  # Remaining time in milliseconds
    turn: str = "white"
    last_move_time: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
    moves: list = field(default_factory=list)
    draw_offer_from: Optional[str] = None
    
    def get_current_player_id(self) -> str:
        """Get the player whose turn it is"""
        return self.white_player_id if self.turn == "white" else self.black_player_id
    
    def get_opponent_id(self, player_id: str) -> str:
        """Get the opponent of a player"""
        if player_id == self.white_player_id:
            return self.black_player_id
        return self.white_player_id
    
    def get_player_color(self, player_id: str) -> Optional[str]:
        """Get the color of a player"""
        if player_id == self.white_player_id:
            return "white"
        elif player_id == self.black_player_id:
            return "black"
        return None


class GameStateManager:
    """Manages all active games in memory"""
    
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self.clock_tasks: Dict[str, asyncio.Task] = {}
    
    def create_game(
        self,
        game_id: str,
        white_player_id: str,
        black_player_id: str,
        base_time: int,
        increment: int
    ) -> GameState:
        """Create a new game state"""
        game = GameState(
            game_id=game_id,
            white_player_id=white_player_id,
            black_player_id=black_player_id,
            engine=ChessEngine(),
            base_time=base_time,
            increment=increment,
            white_time=base_time * 1000,
            black_time=base_time * 1000,
        )
        self.games[game_id] = game
        return game
    
    def get_game(self, game_id: str) -> Optional[GameState]:
        """Get a game by ID"""
        return self.games.get(game_id)
    
    def remove_game(self, game_id: str):
        """Remove a game from memory"""
        if game_id in self.games:
            del self.games[game_id]
        if game_id in self.clock_tasks:
            self.clock_tasks[game_id].cancel()
            del self.clock_tasks[game_id]
    
    def make_move(self, game_id: str, player_id: str, move_uci: str) -> dict:
        """
        Make a move in a game
        
        Returns:
            dict with move result or error
        """
        game = self.games.get(game_id)
        if not game:
            return {"error": "Game not found"}
        
        if not game.is_active:
            return {"error": "Game is not active"}
        
        # Check if it's the player's turn
        if game.get_current_player_id() != player_id:
            return {"error": "Not your turn"}
        
        # Validate and make the move
        if not game.engine.is_legal_move(move_uci):
            return {"error": "Illegal move"}
        
        # Calculate time elapsed
        now = datetime.utcnow()
        elapsed_ms = int((now - game.last_move_time).total_seconds() * 1000)
        
        # Update time
        if game.turn == "white":
            game.white_time -= elapsed_ms
            if game.white_time <= 0:
                game.is_active = False
                return {
                    "result": "0-1",
                    "termination": "timeout",
                    "winner": game.black_player_id
                }
            game.white_time += game.increment * 1000
        else:
            game.black_time -= elapsed_ms
            if game.black_time <= 0:
                game.is_active = False
                return {
                    "result": "1-0",
                    "termination": "timeout",
                    "winner": game.white_player_id
                }
            game.black_time += game.increment * 1000
        
        # Make the move
        result = game.engine.make_move(move_uci)
        game.moves.append(move_uci)
        game.last_move_time = now
        game.turn = "black" if game.turn == "white" else "white"
        game.draw_offer_from = None  # Clear any draw offer
        
        # Check for game end
        if result["is_checkmate"]:
            game.is_active = False
            winner_id = player_id
            winner_result = "1-0" if player_id == game.white_player_id else "0-1"
            return {
                **result,
                "result": winner_result,
                "termination": "checkmate",
                "winner": winner_id,
                "white_time": game.white_time,
                "black_time": game.black_time,
            }
        
        if result["is_stalemate"] or result["is_insufficient_material"]:
            game.is_active = False
            return {
                **result,
                "result": "1/2-1/2",
                "termination": "stalemate" if result["is_stalemate"] else "insufficient",
                "white_time": game.white_time,
                "black_time": game.black_time,
            }
        
        return {
            **result,
            "white_time": game.white_time,
            "black_time": game.black_time,
        }
    
    def resign(self, game_id: str, player_id: str) -> dict:
        """Handle player resignation"""
        game = self.games.get(game_id)
        if not game:
            return {"error": "Game not found"}
        
        if player_id not in [game.white_player_id, game.black_player_id]:
            return {"error": "Not a player in this game"}
        
        game.is_active = False
        winner_id = game.get_opponent_id(player_id)
        result = "1-0" if winner_id == game.white_player_id else "0-1"
        
        return {
            "result": result,
            "termination": "resignation",
            "winner": winner_id,
        }
    
    def offer_draw(self, game_id: str, player_id: str) -> dict:
        """Offer a draw"""
        game = self.games.get(game_id)
        if not game:
            return {"error": "Game not found"}
        
        game.draw_offer_from = player_id
        return {"draw_offered": True}
    
    def accept_draw(self, game_id: str, player_id: str) -> dict:
        """Accept a draw offer"""
        game = self.games.get(game_id)
        if not game:
            return {"error": "Game not found"}
        
        if game.draw_offer_from is None:
            return {"error": "No draw offer pending"}
        
        if game.draw_offer_from == player_id:
            return {"error": "Cannot accept your own draw offer"}
        
        game.is_active = False
        return {
            "result": "1/2-1/2",
            "termination": "agreement",
        }
    
    def decline_draw(self, game_id: str, player_id: str) -> dict:
        """Decline a draw offer"""
        game = self.games.get(game_id)
        if not game:
            return {"error": "Game not found"}
        
        game.draw_offer_from = None
        return {"draw_declined": True}


# Global game state manager instance
game_manager = GameStateManager()
