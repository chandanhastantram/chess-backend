"""WebSocket handler for AI bot games"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
import json

from app.websockets.connection_manager import manager
from app.websockets.game_state import game_manager
from app.services.stockfish_service import StockfishService
from app.utils.auth import decode_access_token

router = APIRouter()

stockfish = StockfishService()

# Difficulty presets mapping to Stockfish skill levels (0-20)
DIFFICULTY_PRESETS = {
    "beginner": 1,
    "easy": 5,
    "medium": 10,
    "hard": 15,
    "expert": 18,
    "master": 20,
}


async def get_user_from_token(token: str) -> Optional[str]:
    """Extract user_id from JWT token"""
    if not token:
        return None
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None


@router.websocket("/ws/game/ai/{game_id}")
async def ai_game_websocket(websocket: WebSocket, game_id: str, token: str = ""):
    """
    WebSocket endpoint for playing against AI bot.
    
    Events received:
    - move: Make a move {"type": "move", "move": "e2e4"}
    - resign: Resign the game {"type": "resign"}
    - new_game: Start new AI game {"type": "new_game", "difficulty": "medium", "time_control": "5+0"}
    
    Events sent:
    - game_state: Full game state on connect
    - move: Player/AI move with updated state
    - ai_move: AI's response move
    - game_over: Game ended with result
    - error: Error message
    """
    # Authenticate user
    user_id = await get_user_from_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(user_id, websocket)
    manager.join_game(user_id, game_id)

    # Default AI settings
    ai_skill_level = 10
    ai_player_id = "AI_BOT"

    # Check if game already exists
    game = game_manager.get_game(game_id)
    if game:
        await manager.send_to_user(user_id, {
            "type": "game_state",
            "fen": game.engine.get_fen(),
            "turn": game.turn,
            "white_time": game.white_time,
            "black_time": game.black_time,
            "moves": game.moves,
            "your_color": game.get_player_color(user_id),
            "is_active": game.is_active,
            "opponent": "AI Bot",
        })

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            event_type = message.get("type")

            if event_type == "new_game":
                # Parse difficulty
                difficulty = message.get("difficulty", "medium")
                if isinstance(difficulty, str):
                    ai_skill_level = DIFFICULTY_PRESETS.get(difficulty, 10)
                elif isinstance(difficulty, int):
                    ai_skill_level = max(0, min(20, difficulty))

                # Parse time control
                tc = message.get("time_control", "5+0")
                parts = tc.split("+")
                base_time = int(parts[0]) * 60
                increment = int(parts[1]) if len(parts) > 1 else 0

                # Player is always white
                player_color = message.get("color", "white")
                if player_color == "white":
                    white_id = user_id
                    black_id = ai_player_id
                else:
                    white_id = ai_player_id
                    black_id = user_id

                game_manager.create_game(
                    game_id=game_id,
                    white_player_id=white_id,
                    black_player_id=black_id,
                    base_time=base_time,
                    increment=increment,
                )

                game = game_manager.get_game(game_id)
                await manager.send_to_user(user_id, {
                    "type": "game_state",
                    "fen": game.engine.get_fen(),
                    "turn": game.turn,
                    "white_time": game.white_time,
                    "black_time": game.black_time,
                    "moves": [],
                    "your_color": game.get_player_color(user_id),
                    "is_active": True,
                    "opponent": "AI Bot",
                    "difficulty": difficulty,
                })

                # If AI plays first (player chose black)
                if player_color == "black":
                    await make_ai_move(user_id, game_id, ai_skill_level)

            elif event_type == "move":
                move = message.get("move")
                if not move:
                    await manager.send_to_user(user_id, {
                        "type": "error",
                        "message": "No move provided"
                    })
                    continue

                result = game_manager.make_move(game_id, user_id, move)

                if "error" in result:
                    await manager.send_to_user(user_id, {
                        "type": "error",
                        "message": result["error"]
                    })
                    continue

                # Send player's move result
                await manager.send_to_user(user_id, {
                    "type": "move",
                    "move": move,
                    **result,
                })

                # Check if game ended
                if "result" in result:
                    await manager.send_to_user(user_id, {
                        "type": "game_over",
                        **result,
                    })
                else:
                    # AI responds
                    await make_ai_move(user_id, game_id, ai_skill_level)

            elif event_type == "resign":
                game = game_manager.get_game(game_id)
                if game:
                    result = game_manager.resign(game_id, user_id)
                    await manager.send_to_user(user_id, {
                        "type": "game_over",
                        **result,
                    })

    except WebSocketDisconnect:
        manager.leave_game(user_id, game_id)
        await manager.disconnect(user_id)


async def make_ai_move(user_id: str, game_id: str, skill_level: int):
    """Have the AI make its move"""
    game = game_manager.get_game(game_id)
    if not game or not game.is_active:
        return

    fen = game.engine.get_fen()
    ai_player_id = "AI_BOT"

    # Get AI's move from Stockfish
    try:
        ai_result = await stockfish.get_best_move(fen, skill_level=skill_level, time_limit=1000)
        ai_move = ai_result.get("best_move")

        if not ai_move:
            # Fallback: pick first legal move
            legal_moves = game.engine.get_legal_moves()
            ai_move = legal_moves[0] if legal_moves else None

        if ai_move:
            # Determine AI's player_id in the game
            ai_game_id = game.white_player_id if game.white_player_id == ai_player_id else game.black_player_id
            result = game_manager.make_move(game_id, ai_game_id, ai_move)

            if "error" not in result:
                await manager.send_to_user(user_id, {
                    "type": "ai_move",
                    "move": ai_move,
                    **result,
                })

                # Check if game ended
                if "result" in result:
                    await manager.send_to_user(user_id, {
                        "type": "game_over",
                        **result,
                    })

    except Exception as e:
        await manager.send_to_user(user_id, {
            "type": "error",
            "message": f"AI error: {str(e)}"
        })
