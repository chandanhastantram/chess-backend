"""Test chess engine"""
import pytest
from app.services.chess_engine import ChessEngine


def test_initial_position():
    """Test initial chess position"""
    engine = ChessEngine()
    assert engine.get_fen() == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


def test_legal_move():
    """Test legal move validation"""
    engine = ChessEngine()
    assert engine.is_legal_move("e2e4") is True
    assert engine.is_legal_move("e2e5") is False


def test_make_move():
    """Test making a move"""
    engine = ChessEngine()
    result = engine.make_move("e2e4")
    
    assert result["san"] == "e4"
    assert result["uci"] == "e2e4"
    assert result["is_check"] is False
    assert result["is_checkmate"] is False
    assert result["is_game_over"] is False


def test_checkmate():
    """Test checkmate detection"""
    # Fool's mate position
    engine = ChessEngine()
    engine.make_move("f2f3")
    engine.make_move("e7e5")
    engine.make_move("g2g4")
    result = engine.make_move("d8h4")
    
    assert result["is_checkmate"] is True
    assert result["is_game_over"] is True


def test_get_legal_moves():
    """Test getting legal moves"""
    engine = ChessEngine()
    legal_moves = engine.get_legal_moves()
    
    assert len(legal_moves) == 20  # 20 legal moves in starting position
    assert "e2e4" in legal_moves
    assert "g1f3" in legal_moves


def test_opening_detection():
    """Test opening detection"""
    engine = ChessEngine()
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"]
    
    for move in moves:
        engine.make_move(move)
    
    opening = engine.detect_opening(moves)
    assert opening is not None
    assert opening["name"] == "Ruy Lopez"
    assert opening["eco"] == "C60"


def test_undo_move():
    """Test undoing a move"""
    engine = ChessEngine()
    initial_fen = engine.get_fen()
    
    engine.make_move("e2e4")
    assert engine.get_fen() != initial_fen
    
    engine.undo_move()
    assert engine.get_fen() == initial_fen
