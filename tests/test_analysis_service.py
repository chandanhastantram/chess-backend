"""Tests for the analysis service"""
import pytest
import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.services.analysis_service import AnalysisService


class TestMoveClassification:
    """Test move classification by centipawn loss"""

    def test_best_move_is_great(self):
        assert AnalysisService.classify_move(0, True) == "great"

    def test_negative_loss_is_brilliant(self):
        assert AnalysisService.classify_move(-100, False) == "brilliant"

    def test_zero_loss_not_best_is_brilliant(self):
        assert AnalysisService.classify_move(0, False) == "brilliant"

    def test_small_loss_is_good(self):
        assert AnalysisService.classify_move(25, False) == "good"

    def test_threshold_good_inaccuracy(self):
        assert AnalysisService.classify_move(30, False) == "good"
        assert AnalysisService.classify_move(31, False) == "inaccuracy"

    def test_threshold_inaccuracy_mistake(self):
        assert AnalysisService.classify_move(100, False) == "inaccuracy"
        assert AnalysisService.classify_move(101, False) == "mistake"

    def test_threshold_mistake_blunder(self):
        assert AnalysisService.classify_move(200, False) == "mistake"
        assert AnalysisService.classify_move(201, False) == "blunder"


class TestEvalToCentipawns:
    """Test Stockfish evaluation conversion"""

    def test_cp_evaluation(self):
        result = AnalysisService.eval_to_centipawns({"type": "cp", "value": 150})
        assert result == 150

    def test_mate_positive(self):
        result = AnalysisService.eval_to_centipawns({"type": "mate", "value": 3})
        assert result == 10000

    def test_mate_negative(self):
        result = AnalysisService.eval_to_centipawns({"type": "mate", "value": -3})
        assert result == -10000

    def test_none_evaluation(self):
        result = AnalysisService.eval_to_centipawns(None)
        assert result is None

    def test_empty_dict(self):
        result = AnalysisService.eval_to_centipawns({})
        assert result is None


class TestAccuracyCalculation:
    """Test overall accuracy calculation"""

    def test_perfect_accuracy(self):
        accuracy = AnalysisService._calculate_accuracy([])
        assert accuracy == 100.0

    def test_zero_loss_high_accuracy(self):
        accuracy = AnalysisService._calculate_accuracy([0, 0, 0])
        assert accuracy > 95.0

    def test_high_loss_low_accuracy(self):
        accuracy = AnalysisService._calculate_accuracy([500, 500, 500])
        assert accuracy < 10.0

    def test_moderate_loss(self):
        accuracy = AnalysisService._calculate_accuracy([30, 30, 30])
        assert 10.0 < accuracy < 100.0

    def test_accuracy_bounded(self):
        accuracy = AnalysisService._calculate_accuracy([10000])
        assert 0 <= accuracy <= 100
