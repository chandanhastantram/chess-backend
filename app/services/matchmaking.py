"""Matchmaking service"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import uuid


@dataclass
class QueueEntry:
    """Represents a player in the matchmaking queue"""
    user_id: str
    rating: int
    time_control: str  # e.g., "5+0", "10+5"
    game_type: str  # "casual" or "rated"
    joined_at: datetime = field(default_factory=datetime.utcnow)
    rating_range: int = 200  # Initial rating range to match


class MatchmakingService:
    """Handles player matchmaking"""
    
    def __init__(self):
        # queue_key -> list of QueueEntry
        # queue_key format: "{time_control}_{game_type}"
        self.queues: Dict[str, List[QueueEntry]] = {}
        self.user_queue: Dict[str, str] = {}  # user_id -> queue_key
        self.pending_matches: Dict[str, Tuple[str, str]] = {}  # match_id -> (user1, user2)
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    def _get_queue_key(self, time_control: str, game_type: str) -> str:
        return f"{time_control}_{game_type}"
    
    async def add_to_queue(
        self,
        user_id: str,
        rating: int,
        time_control: str,
        game_type: str
    ) -> bool:
        """
        Add a player to the matchmaking queue
        
        Returns:
            True if added, False if already in queue
        """
        if user_id in self.user_queue:
            return False
        
        queue_key = self._get_queue_key(time_control, game_type)
        
        if queue_key not in self.queues:
            self.queues[queue_key] = []
        
        entry = QueueEntry(
            user_id=user_id,
            rating=rating,
            time_control=time_control,
            game_type=game_type,
        )
        
        self.queues[queue_key].append(entry)
        self.user_queue[user_id] = queue_key
        
        return True
    
    def remove_from_queue(self, user_id: str) -> bool:
        """
        Remove a player from the matchmaking queue
        
        Returns:
            True if removed, False if not in queue
        """
        if user_id not in self.user_queue:
            return False
        
        queue_key = self.user_queue[user_id]
        if queue_key in self.queues:
            self.queues[queue_key] = [
                e for e in self.queues[queue_key]
                if e.user_id != user_id
            ]
        
        del self.user_queue[user_id]
        return True
    
    def is_in_queue(self, user_id: str) -> bool:
        """Check if a player is in any queue"""
        return user_id in self.user_queue
    
    def get_queue_position(self, user_id: str) -> Optional[int]:
        """Get player's position in queue (1-indexed)"""
        if user_id not in self.user_queue:
            return None
        
        queue_key = self.user_queue[user_id]
        if queue_key in self.queues:
            for i, entry in enumerate(self.queues[queue_key]):
                if entry.user_id == user_id:
                    return i + 1
        return None
    
    def find_match(self, queue_key: str) -> Optional[Tuple[QueueEntry, QueueEntry]]:
        """
        Try to find a match in the specified queue
        
        Returns:
            Tuple of (player1, player2) if match found, None otherwise
        """
        if queue_key not in self.queues:
            return None
        
        queue = self.queues[queue_key]
        if len(queue) < 2:
            return None
        
        # Sort by join time (longest waiting first)
        queue.sort(key=lambda e: e.joined_at)
        
        # Try to match each player with the best available opponent
        for i, player1 in enumerate(queue):
            # Expand rating range based on wait time
            wait_seconds = (datetime.utcnow() - player1.joined_at).total_seconds()
            expanded_range = player1.rating_range + int(wait_seconds / 10) * 50
            expanded_range = min(expanded_range, 500)  # Cap at 500
            
            for j, player2 in enumerate(queue):
                if i == j:
                    continue
                
                # Check if ratings are within range
                rating_diff = abs(player1.rating - player2.rating)
                if rating_diff <= expanded_range:
                    return (player1, player2)
        
        return None
    
    async def process_queues(self) -> List[Tuple[str, str, str]]:
        """
        Process all queues and find matches
        
        Returns:
            List of (match_id, player1_id, player2_id) tuples
        """
        matches = []
        
        for queue_key in list(self.queues.keys()):
            match = self.find_match(queue_key)
            if match:
                player1, player2 = match
                
                # Remove from queue
                self.remove_from_queue(player1.user_id)
                self.remove_from_queue(player2.user_id)
                
                # Create match ID
                match_id = str(uuid.uuid4())
                self.pending_matches[match_id] = (player1.user_id, player2.user_id)
                
                matches.append((match_id, player1.user_id, player2.user_id))
        
        return matches
    
    def get_pending_match(self, match_id: str) -> Optional[Tuple[str, str]]:
        """Get a pending match by ID"""
        return self.pending_matches.get(match_id)
    
    def remove_pending_match(self, match_id: str):
        """Remove a pending match"""
        if match_id in self.pending_matches:
            del self.pending_matches[match_id]
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get number of players in each queue"""
        return {key: len(queue) for key, queue in self.queues.items()}
    
    async def matchmaking_loop(self, callback):
        """
        Background task to continuously process matchmaking
        
        Args:
            callback: Async function to call when match is found
                     callback(match_id, player1_id, player2_id)
        """
        self._running = True
        
        while self._running:
            matches = await self.process_queues()
            
            for match_id, player1_id, player2_id in matches:
                await callback(match_id, player1_id, player2_id)
            
            await asyncio.sleep(1)  # Check every second
    
    def start_matchmaking(self, callback):
        """Start the matchmaking background task"""
        if self._task is None:
            self._task = asyncio.create_task(self.matchmaking_loop(callback))
    
    def stop_matchmaking(self):
        """Stop the matchmaking background task"""
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None


# Global matchmaking service instance
matchmaking_service = MatchmakingService()
