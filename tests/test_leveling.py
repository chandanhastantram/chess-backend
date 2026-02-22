"""Tests for the leveling/XP/streak service"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.services.leveling_service import LevelingService, XP_PER_LEVEL


class TestLevelCalculation:
    """Test level calculation from XP"""

    def test_level_1_at_zero_xp(self):
        assert LevelingService.calculate_level(0) == 1

    def test_level_1_at_99_xp(self):
        assert LevelingService.calculate_level(99) == 1

    def test_level_2_at_100_xp(self):
        assert LevelingService.calculate_level(100) == 2

    def test_level_3_at_200_xp(self):
        assert LevelingService.calculate_level(200) == 3

    def test_level_10_at_900_xp(self):
        assert LevelingService.calculate_level(900) == 10

    def test_large_xp(self):
        assert LevelingService.calculate_level(10000) == 101


class TestXPForNextLevel:
    """Test XP remaining to next level"""

    def test_from_zero(self):
        assert LevelingService.xp_for_next_level(0) == 100

    def test_halfway(self):
        assert LevelingService.xp_for_next_level(50) == 50

    def test_just_leveled_up(self):
        assert LevelingService.xp_for_next_level(100) == 100

    def test_almost_there(self):
        assert LevelingService.xp_for_next_level(199) == 1


class TestXPProgressPercent:
    """Test progress percentage calculation"""

    def test_zero_progress(self):
        assert LevelingService.xp_progress_percent(0) == 0.0

    def test_fifty_percent(self):
        assert LevelingService.xp_progress_percent(50) == 50.0

    def test_at_level_boundary(self):
        assert LevelingService.xp_progress_percent(100) == 0.0

    def test_seventy_five_percent(self):
        assert LevelingService.xp_progress_percent(175) == 75.0


class TestMoveClassification:
    """Test the move classification logic from analysis service"""

    def test_classify_best_move(self):
        from app.services.analysis_service import AnalysisService
        assert AnalysisService.classify_move(0, True) == "great"

    def test_classify_good_move(self):
        from app.services.analysis_service import AnalysisService
        assert AnalysisService.classify_move(20, False) == "good"

    def test_classify_inaccuracy(self):
        from app.services.analysis_service import AnalysisService
        assert AnalysisService.classify_move(80, False) == "inaccuracy"

    def test_classify_mistake(self):
        from app.services.analysis_service import AnalysisService
        assert AnalysisService.classify_move(150, False) == "mistake"

    def test_classify_blunder(self):
        from app.services.analysis_service import AnalysisService
        assert AnalysisService.classify_move(300, False) == "blunder"

    def test_classify_brilliant(self):
        from app.services.analysis_service import AnalysisService
        assert AnalysisService.classify_move(-50, False) == "brilliant"
