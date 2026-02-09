"""Glicko-2 rating system"""
from glicko2 import Player
from typing import Tuple, Dict


class RatingSystem:
    """Glicko-2 rating system implementation"""
    
    # Glicko-2 constants
    TAU = 0.5  # System constant (volatility change)
    EPSILON = 0.000001  # Convergence tolerance
    
    @staticmethod
    def calculate_new_ratings(
        player1_rating: float,
        player1_rd: float,
        player1_vol: float,
        player2_rating: float,
        player2_rd: float,
        player2_vol: float,
        result: float  # 1.0 = player1 wins, 0.5 = draw, 0.0 = player2 wins
    ) -> Tuple[Dict, Dict]:
        """
        Calculate new ratings for both players after a game
        
        Args:
            player1_rating: Player 1's current rating
            player1_rd: Player 1's rating deviation
            player1_vol: Player 1's volatility
            player2_rating: Player 2's current rating
            player2_rd: Player 2's rating deviation
            player2_vol: Player 2's volatility
            result: Game result from player 1's perspective
        
        Returns:
            Tuple of (player1_new_ratings, player2_new_ratings)
        """
        # Create Glicko2 player objects
        p1 = Player(rating=player1_rating, rd=player1_rd, vol=player1_vol)
        p2 = Player(rating=player2_rating, rd=player2_rd, vol=player2_vol)
        
        # Update player 1's rating
        p1.update_player([p2.rating], [p2.rd], [result])
        
        # Update player 2's rating (inverse result)
        p2.update_player([p1.rating], [p1.rd], [1.0 - result])
        
        return (
            {
                "rating": int(p1.rating),
                "rating_deviation": p1.rd,
                "volatility": p1.vol,
            },
            {
                "rating": int(p2.rating),
                "rating_deviation": p2.rd,
                "volatility": p2.vol,
            }
        )
    
    @staticmethod
    def get_expected_score(rating1: float, rd1: float, rating2: float, rd2: float) -> float:
        """
        Calculate expected score for player 1 against player 2
        
        Args:
            rating1: Player 1's rating
            rd1: Player 1's rating deviation
            rating2: Player 2's rating
            rd2: Player 2's rating deviation
        
        Returns:
            Expected score (0.0 to 1.0)
        """
        import math
        
        # Glicko-2 scale factor
        Q = math.log(10) / 400
        
        # Calculate g(RD)
        g_rd2 = 1 / math.sqrt(1 + 3 * Q**2 * rd2**2 / math.pi**2)
        
        # Calculate expected score
        exponent = -g_rd2 * (rating1 - rating2) / 400
        expected = 1 / (1 + 10**exponent)
        
        return expected
    
    @staticmethod
    def get_rating_change(
        current_rating: float,
        opponent_rating: float,
        result: float,
        k_factor: int = 32
    ) -> int:
        """
        Simple ELO-style rating change calculation (for display purposes)
        
        Args:
            current_rating: Current player rating
            opponent_rating: Opponent's rating
            result: Game result (1.0 = win, 0.5 = draw, 0.0 = loss)
            k_factor: K-factor for rating change magnitude
        
        Returns:
            Rating change (positive or negative)
        """
        import math
        
        expected = 1 / (1 + 10**((opponent_rating - current_rating) / 400))
        change = k_factor * (result - expected)
        
        return int(round(change))
