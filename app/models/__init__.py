"""Database models"""
from app.models.user import User
from app.models.rating import Rating
from app.models.game import Game
from app.models.move import Move
from app.models.puzzle import Puzzle, PuzzleAttempt
from app.models.tournament import Tournament, TournamentParticipant, TournamentPairing
from app.models.friendship import Friendship
from app.models.player_stats import PlayerStats
from app.models.game_analysis import GameAnalysis, MoveAnalysis
from app.models.challenge import Challenge

__all__ = [
    "User",
    "Rating",
    "Game",
    "Move",
    "Puzzle",
    "PuzzleAttempt",
    "Tournament",
    "TournamentParticipant",
    "TournamentPairing",
    "Friendship",
    "PlayerStats",
    "GameAnalysis",
    "MoveAnalysis",
    "Challenge",
]
