"""WebSocket connection manager"""
from fastapi import WebSocket
from typing import Dict, Set, Optional
import json
import asyncio


class ConnectionManager:
    """Manages WebSocket connections for real-time chess games"""
    
    def __init__(self):
        # user_id -> WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}
        # game_id -> set of user_ids in the game
        self.game_rooms: Dict[str, Set[str]] = {}
        # user_id -> game_id (current game)
        self.user_games: Dict[str, str] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept and register a WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    async def disconnect(self, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove from game room
        if user_id in self.user_games:
            game_id = self.user_games[user_id]
            if game_id in self.game_rooms:
                self.game_rooms[game_id].discard(user_id)
            del self.user_games[user_id]
    
    def join_game(self, user_id: str, game_id: str):
        """Add user to a game room"""
        if game_id not in self.game_rooms:
            self.game_rooms[game_id] = set()
        self.game_rooms[game_id].add(user_id)
        self.user_games[user_id] = game_id
    
    def leave_game(self, user_id: str, game_id: str):
        """Remove user from a game room"""
        if game_id in self.game_rooms:
            self.game_rooms[game_id].discard(user_id)
        if user_id in self.user_games:
            del self.user_games[user_id]
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception:
                await self.disconnect(user_id)
    
    async def broadcast_to_game(self, game_id: str, message: dict, exclude: Optional[str] = None):
        """Broadcast message to all users in a game room"""
        if game_id in self.game_rooms:
            for user_id in self.game_rooms[game_id]:
                if user_id != exclude:
                    await self.send_to_user(user_id, message)
    
    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in self.active_connections:
            await self.send_to_user(user_id, message)
    
    def is_connected(self, user_id: str) -> bool:
        """Check if a user is connected"""
        return user_id in self.active_connections
    
    def get_game_users(self, game_id: str) -> Set[str]:
        """Get all users in a game room"""
        return self.game_rooms.get(game_id, set())
    
    def get_user_count(self) -> int:
        """Get total number of connected users"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
