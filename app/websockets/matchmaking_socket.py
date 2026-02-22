"""WebSocket handlers for matchmaking"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Optional
import json

from app.websockets.connection_manager import manager
from app.websockets.game_state import game_manager
from app.services.matchmaking import matchmaking_service
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


async def on_match_found(match_id: str, player1_id: str, player2_id: str):
    """Callback when a match is found"""
    # Notify both players
    await manager.send_to_user(player1_id, {
        "type": "match_found",
        "match_id": match_id,
        "opponent_id": player2_id,
    })
    
    await manager.send_to_user(player2_id, {
        "type": "match_found",
        "match_id": match_id,
        "opponent_id": player1_id,
    })


@router.websocket("/ws/matchmaking")
async def matchmaking_websocket(websocket: WebSocket, token: str = ""):
    """
    WebSocket endpoint for matchmaking
    
    Events received:
    - join_queue: Join matchmaking queue
        {"type": "join_queue", "time_control": "5+0", "game_type": "rated", "rating": 1500}
    - leave_queue: Leave matchmaking queue
        {"type": "leave_queue"}
    - accept_match: Accept a found match
        {"type": "accept_match", "match_id": "..."}
    
    Events sent:
    - queue_joined: Successfully joined queue
        {"type": "queue_joined", "position": 1}
    - queue_left: Left the queue
        {"type": "queue_left"}
    - match_found: A match was found
        {"type": "match_found", "match_id": "...", "opponent_id": "..."}
    - game_created: Game is ready to start
        {"type": "game_created", "game_id": "...", "color": "white"}
    - error: Error message
        {"type": "error", "message": "..."}
    """
    # Authenticate user
    user_id = await get_user_from_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await manager.connect(user_id, websocket)
    
    # Start matchmaking loop if not already running
    matchmaking_service.start_matchmaking(on_match_found)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            event_type = message.get("type")
            
            if event_type == "join_queue":
                time_control = message.get("time_control", "5+0")
                game_type = message.get("game_type", "rated")
                rating = message.get("rating", 1500)
                
                success = await matchmaking_service.add_to_queue(
                    user_id, rating, time_control, game_type
                )
                
                if success:
                    position = matchmaking_service.get_queue_position(user_id)
                    await manager.send_to_user(user_id, {
                        "type": "queue_joined",
                        "position": position,
                        "time_control": time_control,
                        "game_type": game_type,
                    })
                else:
                    await manager.send_to_user(user_id, {
                        "type": "error",
                        "message": "Already in queue"
                    })
            
            elif event_type == "leave_queue":
                success = matchmaking_service.remove_from_queue(user_id)
                if success:
                    await manager.send_to_user(user_id, {
                        "type": "queue_left"
                    })
            
            elif event_type == "accept_match":
                match_id = message.get("match_id")
                if not match_id:
                    await manager.send_to_user(user_id, {
                        "type": "error",
                        "message": "No match_id provided"
                    })
                    continue
                
                match = matchmaking_service.get_pending_match(match_id)
                if not match:
                    await manager.send_to_user(user_id, {
                        "type": "error",
                        "message": "Match not found or expired"
                    })
                    continue
                
                player1_id, player2_id = match
                if user_id not in [player1_id, player2_id]:
                    await manager.send_to_user(user_id, {
                        "type": "error",
                        "message": "Not a player in this match"
                    })
                    continue
                
                # Create the game
                game_id = match_id  # Use match_id as game_id for simplicity
                
                # Parse time control from queue entry (e.g., "5+0" -> base=5min, increment=0)
                queue_entry = matchmaking_service.user_queue.get(player1_id)
                tc_str = "5+0"
                if queue_entry:
                    queue_key = queue_entry
                    tc_str = queue_key.split("_")[0] if "_" in queue_key else "5+0"
                tc_parts = tc_str.split("+")
                base_time = int(tc_parts[0]) * 60      # minutes -> seconds
                increment = int(tc_parts[1]) if len(tc_parts) > 1 else 0
                
                # Create game state
                game_manager.create_game(
                    game_id=game_id,
                    white_player_id=player1_id,
                    black_player_id=player2_id,
                    base_time=base_time,
                    increment=increment,
                )
                
                # Remove pending match
                matchmaking_service.remove_pending_match(match_id)
                
                # Notify both players
                await manager.send_to_user(player1_id, {
                    "type": "game_created",
                    "game_id": game_id,
                    "color": "white",
                    "opponent_id": player2_id,
                })
                
                await manager.send_to_user(player2_id, {
                    "type": "game_created",
                    "game_id": game_id,
                    "color": "black",
                    "opponent_id": player1_id,
                })
    
    except WebSocketDisconnect:
        matchmaking_service.remove_from_queue(user_id)
        await manager.disconnect(user_id)
