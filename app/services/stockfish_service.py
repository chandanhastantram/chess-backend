"""Stockfish AI service"""
from stockfish import Stockfish
from typing import Dict, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.config import settings


class StockfishService:
    """Stockfish chess engine integration with async support"""
    
    def __init__(self, stockfish_path: str = None):
        """
        Initialize Stockfish service
        
        Args:
            stockfish_path: Path to Stockfish executable
        """
        self.stockfish_path = stockfish_path or settings.STOCKFISH_PATH
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def get_best_move(
        self,
        fen: str,
        skill_level: int = 20,
        time_limit: int = 1000
    ) -> Dict:
        """
        Get best move from Stockfish asynchronously
        
        Args:
            fen: FEN position
            skill_level: Stockfish skill level (0-20)
            time_limit: Time limit in milliseconds
        
        Returns:
            Dict with best_move and evaluation
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._get_best_move_sync,
            fen,
            skill_level,
            time_limit
        )
    
    def _get_best_move_sync(
        self,
        fen: str,
        skill_level: int,
        time_limit: int
    ) -> Dict:
        """Synchronous version of get_best_move"""
        try:
            stockfish = Stockfish(
                path=self.stockfish_path,
                parameters={"Threads": 2, "Hash": 2048}
            )
            stockfish.set_skill_level(skill_level)
            stockfish.set_fen_position(fen)
            
            best_move = stockfish.get_best_move_time(time_limit)
            evaluation = stockfish.get_evaluation()
            
            return {
                "best_move": best_move,
                "evaluation": evaluation,
            }
        except Exception as e:
            return {
                "best_move": None,
                "evaluation": None,
                "error": str(e)
            }
    
    async def analyze_position(
        self,
        fen: str,
        depth: int = 20
    ) -> Dict:
        """
        Deep analysis of position
        
        Args:
            fen: FEN position
            depth: Search depth
        
        Returns:
            Dict with evaluation, best_move, and top_moves
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._analyze_position_sync,
            fen,
            depth
        )
    
    def _analyze_position_sync(self, fen: str, depth: int) -> Dict:
        """Synchronous version of analyze_position"""
        try:
            stockfish = Stockfish(self.stockfish_path)
            stockfish.set_fen_position(fen)
            stockfish.set_depth(depth)
            
            return {
                "evaluation": stockfish.get_evaluation(),
                "best_move": stockfish.get_best_move(),
                "top_moves": stockfish.get_top_moves(5),
            }
        except Exception as e:
            return {
                "evaluation": None,
                "best_move": None,
                "top_moves": [],
                "error": str(e)
            }
    
    async def evaluate_move(
        self,
        fen: str,
        move: str,
        depth: int = 15
    ) -> Dict:
        """
        Evaluate a specific move
        
        Args:
            fen: FEN position before move
            move: Move in UCI format
            depth: Search depth
        
        Returns:
            Dict with move evaluation
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._evaluate_move_sync,
            fen,
            move,
            depth
        )
    
    def _evaluate_move_sync(self, fen: str, move: str, depth: int) -> Dict:
        """Synchronous version of evaluate_move"""
        try:
            stockfish = Stockfish(self.stockfish_path)
            stockfish.set_fen_position(fen)
            stockfish.set_depth(depth)
            
            # Get best move
            best_move = stockfish.get_best_move()
            
            # Make the player's move
            stockfish.make_moves_from_current_position([move])
            evaluation_after = stockfish.get_evaluation()
            
            return {
                "move": move,
                "is_best": move == best_move,
                "evaluation": evaluation_after,
                "best_move": best_move,
            }
        except Exception as e:
            return {
                "move": move,
                "is_best": False,
                "evaluation": None,
                "error": str(e)
            }
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)
