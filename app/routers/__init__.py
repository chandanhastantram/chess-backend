"""Routers package"""
from app.routers import auth, users, games, puzzles, tournaments
from app.routers import leaderboard, board_themes, offline, analysis, challenges

__all__ = [
    "auth", "users", "games", "puzzles", "tournaments",
    "leaderboard", "board_themes", "offline", "analysis", "challenges",
]
