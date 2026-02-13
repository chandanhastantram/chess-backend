"""Chess engine service using python-chess"""
import chess
import chess.pgn
from typing import List, Dict, Optional
from io import StringIO


class ChessEngine:
    """Chess game logic using python-chess library"""
    
    def __init__(self, fen: Optional[str] = None):
        """Initialize chess board from FEN or starting position"""
        self.board = chess.Board(fen) if fen else chess.Board()
    
    def is_legal_move(self, move_uci: str) -> bool:
        """Check if a move is legal"""
        try:
            move = chess.Move.from_uci(move_uci)
            return move in self.board.legal_moves
        except ValueError:
            return False
    
    def make_move(self, move_uci: str) -> Dict:
        """
        Make a move and return the new game state
        
        Args:
            move_uci: Move in UCI format (e.g., "e2e4")
        
        Returns:
            Dict with game state information
        
        Raises:
            ValueError: If move is illegal
        """
        move = chess.Move.from_uci(move_uci)
        if move not in self.board.legal_moves:
            raise ValueError(f"Illegal move: {move_uci}")    
 
        san = self.board.san(move) 
        
        # Make the move
        self.board.push(move)
        
        return {
            "fen": self.board.fen(),
            "san": san,
            "uci": move_uci,
            "is_check": self.board.is_check(),
            "is_checkmate": self.board.is_checkmate(),
            "is_stalemate": self.board.is_stalemate(),
            "is_insufficient_material": self.board.is_insufficient_material(),
            "is_fifty_moves": self.board.is_fifty_moves(),
            "is_repetition": self.board.is_repetition(3),
            "is_game_over": self.board.is_game_over(),
        }
    
    def get_legal_moves(self) -> List[str]:
        """Get all legal moves in UCI format"""
        return [move.uci() for move in self.board.legal_moves]
    
    def get_game_status(self) -> Dict:
        """Get current game status"""
        return {
            "is_game_over": self.board.is_game_over(),
            "is_checkmate": self.board.is_checkmate(),
            "is_stalemate": self.board.is_stalemate(),
            "is_insufficient_material": self.board.is_insufficient_material(),
            "is_fifty_moves": self.board.is_fifty_moves(),
            "is_repetition": self.board.is_repetition(3),
            "result": self.board.result(),
            "turn": "white" if self.board.turn == chess.WHITE else "black",
        }
    
    def get_fen(self) -> str:
        """Get current FEN position"""
        return self.board.fen()
    
    def get_pgn(self, white_player: str = "White", black_player: str = "Black", result: str = "*") -> str:
        """
        Generate PGN from current game
        
        Args:
            white_player: White player name
            black_player: Black player name
            result: Game result (1-0, 0-1, 1/2-1/2, *)
        
        Returns:
            PGN string
        """
        game = chess.pgn.Game()
        game.headers["White"] = white_player
        game.headers["Black"] = black_player
        game.headers["Result"] = result
        
        # Add moves
        node = game
        board = chess.Board()
        for move in self.board.move_stack:
            node = node.add_variation(move)
        
        # Convert to string
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        pgn_string = game.accept(exporter)
        
        return pgn_string
    
    def detect_opening(self, moves: List[str]) -> Optional[Dict[str, str]]:
        """
        Detect chess opening from move sequence
        
        Args:
            moves: List of moves in UCI format
        
        Returns:
            Dict with opening name and ECO code, or None
        """
        # Basic opening detection (can be expanded with full opening database)
        openings = {
            ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5"): {"name": "Ruy Lopez", "eco": "C60"},
            ("e2e4", "c7c5"): {"name": "Sicilian Defense", "eco": "B20"},
            ("d2d4", "d7d5", "c2c4"): {"name": "Queen's Gambit", "eco": "D06"},
            ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4"): {"name": "Italian Game", "eco": "C50"},
            ("d2d4", "g8f6", "c2c4", "e7e6"): {"name": "Queen's Indian Defense", "eco": "E12"},
        }
        
        # Check for matching opening
        for i in range(min(len(moves), 5), 0, -1):
            move_tuple = tuple(moves[:i])
            if move_tuple in openings:
                return openings[move_tuple]
        
        return None
    
    def undo_move(self) -> bool:
        """
        Undo the last move
        
        Returns:
            True if successful, False if no moves to undo
        """
        try:
            self.board.pop()
            return True
        except IndexError:
            return False
    
    def reset(self):
        """Reset board to starting position"""
        self.board.reset()
