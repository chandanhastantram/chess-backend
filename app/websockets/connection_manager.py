"""WebSocket connection manager with spectator and online presence support"""
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
        # game_id -> set of spectator user_ids
        self.spectators: Dict[str, Set[str]] = {}
        # All online user_ids
        self.online_users: Set[str] = set()
    
    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept and register a WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.online_users.add(user_id)
    
    async def disconnect(self, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        self.online_users.discard(user_id)
        
        # Remove from game room
        if user_id in self.user_games:
            game_id = self.user_games[user_id]
            if game_id in self.game_rooms:
                self.game_rooms[game_id].discard(user_id)
            del self.user_games[user_id]
        
        # Remove from spectator rooms
        for game_id, specs in list(self.spectators.items()):
            specs.discard(user_id)
            if not specs:
                del self.spectators[game_id]
    
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
    
    # --- Spectator methods ---
    
    def add_spectator(self, user_id: str, game_id: str):
        """Add a spectator to a game room"""
        if game_id not in self.spectators:
            self.spectators[game_id] = set()
        self.spectators[game_id].add(user_id)
    
    def remove_spectator(self, user_id: str, game_id: str):
        """Remove a spectator from a game room"""
        if game_id in self.spectators:
            self.spectators[game_id].discard(user_id)
            if not self.spectators[game_id]:
                del self.spectators[game_id]
    
    def get_spectators(self, game_id: str) -> Set[str]:
        """Get all spectators for a game"""
        return self.spectators.get(game_id, set())
    
    def get_spectator_count(self, game_id: str) -> int:
        """Get the number of spectators watching a game"""
        return len(self.spectators.get(game_id, set()))
    
    def is_spectator(self, user_id: str, game_id: str) -> bool:
        """Check if a user is spectating a game"""
        return user_id in self.spectators.get(game_id, set())
    
    # --- Online presence ---
    
    def is_online(self, user_id: str) -> bool:
        """Check if a user is online"""
        return user_id in self.online_users
    
    def get_online_users(self) -> Set[str]:
        """Get all online user IDs"""
        return self.online_users.copy()
    
    # --- Messaging ---
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception:
                await self.disconnect(user_id)
    
    async def broadcast_to_game(self, game_id: str, message: dict, exclude: Optional[str] = None):
        """Broadcast message to all players AND spectators in a game room"""
        # Send to players
        if game_id in self.game_rooms:
            for user_id in self.game_rooms[game_id]:
                if user_id != exclude:
                    await self.send_to_user(user_id, message)
        
        # Send to spectators
        if game_id in self.spectators:
            for user_id in self.spectators[game_id]:
                if user_id != exclude:
                    await self.send_to_user(user_id, message)
    
    async def broadcast_to_spectators(self, game_id: str, message: dict):
        """Broadcast message only to spectators of a game"""
        if game_id in self.spectators:
            for user_id in self.spectators[game_id]:
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
