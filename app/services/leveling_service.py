"""Leveling service for XP, levels, and streaks"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from typing import Optional, Dict
from app.models.player_stats import PlayerStats


XP_REWARDS = {
    "win": 25,
    "draw": 10,
    "loss": 5,
    "puzzle_solved": 15,
    "puzzle_failed": 3,
    "tournament_win": 50,
    "daily_login": 5,
}

# XP required per level (level * 100)
XP_PER_LEVEL = 100


class LevelingService:
    """Handles XP, leveling, and streak tracking"""

    @staticmethod
    def calculate_level(xp: int) -> int:
        """Calculate level from total XP"""
        return max(1, (xp // XP_PER_LEVEL) + 1)

    @staticmethod
    def xp_for_next_level(current_xp: int) -> int:
        """XP needed to reach the next level"""
        current_level = LevelingService.calculate_level(current_xp)
        return (current_level * XP_PER_LEVEL) - current_xp

    @staticmethod
    def xp_progress_percent(current_xp: int) -> float:
        """Progress percentage toward next level (0-100)"""
        xp_in_current_level = current_xp % XP_PER_LEVEL
        return (xp_in_current_level / XP_PER_LEVEL) * 100

    @staticmethod
    async def get_or_create_stats(user_id, db: AsyncSession) -> PlayerStats:
        """Get or create player stats for a user"""
        result = await db.execute(
            select(PlayerStats).where(PlayerStats.user_id == user_id)
        )
        stats = result.scalar_one_or_none()

        if not stats:
            stats = PlayerStats(user_id=user_id)
            db.add(stats)
            await db.flush()

        return stats

    @staticmethod
    async def award_xp(user_id, xp_amount: int, db: AsyncSession) -> Dict:
        """
        Award XP to a player and handle level-ups.

        Returns:
            Dict with xp_gained, new_xp, new_level, leveled_up
        """
        stats = await LevelingService.get_or_create_stats(user_id, db)

        old_level = stats.level
        stats.xp += xp_amount
        stats.level = LevelingService.calculate_level(stats.xp)

        leveled_up = stats.level > old_level

        return {
            "xp_gained": xp_amount,
            "total_xp": stats.xp,
            "level": stats.level,
            "leveled_up": leveled_up,
            "xp_to_next_level": LevelingService.xp_for_next_level(stats.xp),
            "progress_percent": round(LevelingService.xp_progress_percent(stats.xp), 1),
        }

    @staticmethod
    async def update_streak(user_id, result: str, db: AsyncSession) -> Dict:
        """
        Update win/loss/daily streaks after a game.

        Args:
            result: "win", "loss", or "draw"

        Returns:
            Dict with streak info
        """
        stats = await LevelingService.get_or_create_stats(user_id, db)
        today = date.today()

        # Daily streak
        if stats.last_played_date:
            days_diff = (today - stats.last_played_date).days
            if days_diff == 1:
                stats.daily_streak += 1
            elif days_diff > 1:
                stats.daily_streak = 1
            # Same day: no change to daily streak
        else:
            stats.daily_streak = 1

        stats.last_played_date = today
        stats.games_today += 1

        # Win/loss streaks
        if result == "win":
            stats.current_win_streak += 1
            stats.current_loss_streak = 0
            if stats.current_win_streak > stats.best_win_streak:
                stats.best_win_streak = stats.current_win_streak
        elif result == "loss":
            stats.current_loss_streak += 1
            stats.current_win_streak = 0
        else:  # draw
            stats.current_win_streak = 0
            stats.current_loss_streak = 0

        return {
            "current_win_streak": stats.current_win_streak,
            "best_win_streak": stats.best_win_streak,
            "current_loss_streak": stats.current_loss_streak,
            "daily_streak": stats.daily_streak,
            "games_today": stats.games_today,
        }

    @staticmethod
    async def get_level_info(user_id, db: AsyncSession) -> Optional[Dict]:
        """Get a user's level, XP, and streak info"""
        stats = await LevelingService.get_or_create_stats(user_id, db)

        return {
            "level": stats.level,
            "xp": stats.xp,
            "xp_to_next_level": LevelingService.xp_for_next_level(stats.xp),
            "progress_percent": round(LevelingService.xp_progress_percent(stats.xp), 1),
            "current_win_streak": stats.current_win_streak,
            "best_win_streak": stats.best_win_streak,
            "current_loss_streak": stats.current_loss_streak,
            "daily_streak": stats.daily_streak,
            "games_today": stats.games_today,
        }
