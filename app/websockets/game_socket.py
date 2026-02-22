"""WebSocket handlers for real-time chess games"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Optional
import json

from app.websockets.connection_manager import manager
from app.websockets.game_state import game_manager
from app.utils.auth import decode_access_token

router = APIRouter()


async def get_user_from_token(token: str) -> Optional[str]:
    """Extract user_id from JWT token"""
    if not token:
        return None
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None


@router.websocket("/ws/game/{game_id}")
async def game_websocket(websocket: WebSocket, game_id: str, token: str = ""):
    """
    WebSocket endpoint for real-time chess game
    
    Events received:
    - move: Make a move {"type": "move", "move": "e2e4"}
    - resign: Resign the game {"type": "resign"}
    - offer_draw: Offer a draw {"type": "offer_draw"}
    - accept_draw: Accept draw offer {"type": "accept_draw"}
    - decline_draw: Decline draw offer {"type": "decline_draw"}
    - chat: Send chat message {"type": "chat", "message": "..."}
    
    Events sent:
    - game_state: Full game state on connect
    - move: Opponent's move with updated state
    - game_over: Game ended with result
    - draw_offered: Opponent offered a draw
    - draw_declined: Draw was declined
    - chat: Chat message received
    - error: Error message
    """
    # Authenticate user
    user_id = await get_user_from_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    # Connect and join game room
    await manager.connect(user_id, websocket)
    
    # Determine if user is a player or spectator
    game = game_manager.get_game(game_id)
    is_spectator = False
    if game:
        player_color = game.get_player_color(user_id)
        if player_color is None:
            # User is not a player — join as spectator
            is_spectator = True
            manager.add_spectator(user_id, game_id)
            await manager.broadcast_to_game(game_id, {
                "type": "spectator_joined",
                "user_id": user_id,
                "spectator_count": manager.get_spectator_count(game_id),
            })
        else:
            manager.join_game(user_id, game_id)
    else:
        manager.join_game(user_id, game_id)
    
    # Send initial game state if game exists
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
            "is_spectator": is_spectator,
            "spectator_count": manager.get_spectator_count(game_id),
        })
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            event_type = message.get("type")
            
            # Block spectator actions (they can only send chat)
            if is_spectator and event_type in ("move", "resign", "offer_draw", "accept_draw", "decline_draw"):
                await manager.send_to_user(user_id, {
                    "type": "error",
                    "message": "Spectators cannot perform game actions"
                })
                continue
            
            if event_type == "move":
                await handle_move(user_id, game_id, message.get("move"))
            
            elif event_type == "resign":
                await handle_resign(user_id, game_id)
            
            elif event_type == "offer_draw":
                await handle_offer_draw(user_id, game_id)
            
            elif event_type == "accept_draw":
                await handle_accept_draw(user_id, game_id)
            
            elif event_type == "decline_draw":
                await handle_decline_draw(user_id, game_id)
            
            elif event_type == "chat":
                await handle_chat(user_id, game_id, message.get("message", ""))
            
    except WebSocketDisconnect:
        if is_spectator:
            manager.remove_spectator(user_id, game_id)
            await manager.broadcast_to_game(game_id, {
                "type": "spectator_left",
                "user_id": user_id,
                "spectator_count": manager.get_spectator_count(game_id),
            })
        else:
            manager.leave_game(user_id, game_id)
        await manager.disconnect(user_id)
        
        # Notify opponent of disconnect
        await manager.broadcast_to_game(game_id, {
            "type": "opponent_disconnected",
            "user_id": user_id,
        })


async def handle_move(user_id: str, game_id: str, move: str):
    """Handle a move from a player"""
    if not move:
        await manager.send_to_user(user_id, {
            "type": "error",
            "message": "No move provided"
        })
        return
    
    result = game_manager.make_move(game_id, user_id, move)
    
    if "error" in result:
        await manager.send_to_user(user_id, {
            "type": "error",
            "message": result["error"]
        })
        return
    
    # Check if game ended
    if "result" in result:
        # Game over
        await manager.broadcast_to_game(game_id, {
            "type": "game_over",
            **result,
        })
    else:
        # Normal move - broadcast to all players
        await manager.broadcast_to_game(game_id, {
            "type": "move",
            "move": move,
            **result,
        })


async def handle_resign(user_id: str, game_id: str):
    """Handle resignation"""
    result = game_manager.resign(game_id, user_id)
    
    if "error" in result:
        await manager.send_to_user(user_id, {
            "type": "error",
            "message": result["error"]
        })
        return
    
    await manager.broadcast_to_game(game_id, {
        "type": "game_over",
        **result,
    })


async def handle_offer_draw(user_id: str, game_id: str):
    """Handle draw offer"""
    result = game_manager.offer_draw(game_id, user_id)
    
    if "error" in result:
        await manager.send_to_user(user_id, {
            "type": "error",
            "message": result["error"]
        })
        return
    
    game = game_manager.get_game(game_id)
    if game:
        opponent_id = game.get_opponent_id(user_id)
        await manager.send_to_user(opponent_id, {
            "type": "draw_offered",
            "from": user_id,
        })


async def handle_accept_draw(user_id: str, game_id: str):
    """Handle accepting a draw"""
    result = game_manager.accept_draw(game_id, user_id)
    
    if "error" in result:
        await manager.send_to_user(user_id, {
            "type": "error",
            "message": result["error"]
        })
        return
    
    await manager.broadcast_to_game(game_id, {
        "type": "game_over",
        **result,
    })


async def handle_decline_draw(user_id: str, game_id: str):
    """Handle declining a draw"""
    result = game_manager.decline_draw(game_id, user_id)
    
    if "error" in result:
        await manager.send_to_user(user_id, {
            "type": "error",
            "message": result["error"]
        })
        return
    
    game = game_manager.get_game(game_id)
    if game:
        opponent_id = game.get_opponent_id(user_id)
        await manager.send_to_user(opponent_id, {
            "type": "draw_declined",
        })


async def handle_chat(user_id: str, game_id: str, message: str):
    """Handle chat message"""
    if not message or len(message) > 500:
        return
    
    await manager.broadcast_to_game(game_id, {
        "type": "chat",
        "from": user_id,
        "message": message,
    }, exclude=user_id)
