"""Tournament pairing service"""
from typing import List, Dict, Tuple, Optional
import random


class TournamentService:
    """Swiss and Round-Robin tournament pairing algorithms"""
    
    @staticmethod
    def generate_swiss_pairings(
        participants: List[Dict],
        round_number: int,
        previous_pairings: List[Tuple[str, str]]
    ) -> List[Tuple[str, Optional[str]]]:
        """
        Generate Swiss system pairings
        
        Args:
            participants: List of {user_id, score, rating, color_balance}
            round_number: Current round number
            previous_pairings: List of (white_id, black_id) from previous rounds
        
        Returns:
            List of (white_player_id, black_player_id) tuples (black can be None for bye)
        """
        # Sort by score (descending), then rating (descending)
        sorted_participants = sorted(
            participants,
            key=lambda p: (-p['score'], -p['rating'])    
        )
        
        # Group by score
        score_groups = {}
        for p in sorted_participants:
            score = p['score']
            if score not in score_groups:
                score_groups[score] = []
            score_groups[score].append(p)
        
        pairings = []
        unpaired = []
        
        # Process each score group
        for score in sorted(score_groups.keys(), reverse=True):
            group = score_groups[score]
            group_with_unpaired = unpaired + group
            unpaired = []
            
            # Sort by rating within group
            group_with_unpaired.sort(key=lambda p: p['rating'], reverse=True)
            
            # Pair top half with bottom half
            while len(group_with_unpaired) >= 2:
                mid = len(group_with_unpaired) // 2
                
                # Try to pair first player from top half
                player1 = group_with_unpaired[0]
                paired = False
                
                # Try pairing with players from bottom half
                for i in range(mid, len(group_with_unpaired)):
                    player2 = group_with_unpaired[i]
                    
                    # Check if they've played before
                    if (player1['user_id'], player2['user_id']) in previous_pairings or \
                       (player2['user_id'], player1['user_id']) in previous_pairings:
                        continue
                    
                    # Determine colors based on color balance
                    if player1['color_balance'] <= player2['color_balance']:
                        white, black = player1, player2
                    else:
                        white, black = player2, player1
                    
                    pairings.append((white['user_id'], black['user_id']))
                    
                    # Remove paired players
                    group_with_unpaired.remove(player1)
                    group_with_unpaired.remove(player2)
                    paired = True
                    break
                
                if not paired:
                    # Couldn't pair this player, move to unpaired
                    unpaired.append(player1)
                    group_with_unpaired.remove(player1)
        
        # Give bye to unpaired player (if any)
        if unpaired:
            pairings.append((unpaired[0]['user_id'], None))
        
        return pairings
    
    @staticmethod
    def generate_round_robin_pairings(
        participant_ids: List[str],
        total_rounds: Optional[int] = None
    ) -> Dict[int, List[Tuple[str, Optional[str]]]]:
        """
        Generate complete round-robin schedule using circle method
        
        Args:
            participant_ids: List of participant user IDs
            total_rounds: Number of rounds (defaults to n-1 for even, n for odd)
        
        Returns:
            Dict mapping round_number to list of pairings
        """
        n = len(participant_ids)
        players = participant_ids.copy()
        
        # Add dummy player if odd number
        if n % 2 == 1:
            players.append(None)
            n += 1
        
        if total_rounds is None:
            total_rounds = n - 1
        
        rounds = {}
        
        for round_num in range(1, total_rounds + 1):
            round_pairings = []
            
            # Pair players
            for i in range(n // 2):
                player1 = players[i]
                player2 = players[n - 1 - i]
                
                if player1 is not None and player2 is not None:
                    # Alternate colors
                    if round_num % 2 == 0:
                        round_pairings.append((player1, player2))
                    else:
                        round_pairings.append((player2, player1))
                elif player1 is not None:
                    round_pairings.append((player1, None))  # Bye
                elif player2 is not None:
                    round_pairings.append((player2, None))  # Bye
            
            rounds[round_num] = round_pairings
            
            # Rotate players (keep first player fixed)
            players = [players[0]] + [players[-1]] + players[1:-1]
        
        return rounds
    
    @staticmethod
    def calculate_tiebreaks(
        participant_scores: Dict[str, float],
        participant_opponents: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate tiebreak scores (Buchholz, Sonneborn-Berger)
        
        Args:
            participant_scores: Dict of user_id -> score
            participant_opponents: Dict of user_id -> list of opponent user_ids
        
        Returns:
            Dict of user_id -> {buchholz, sonneborn_berger}
        """
        tiebreaks = {}
        
        for user_id in participant_scores:
            opponents = participant_opponents.get(user_id, [])
            
            # Buchholz: Sum of opponents' scores
            buchholz = sum(participant_scores.get(opp, 0) for opp in opponents)
            
            # Sonneborn-Berger: Sum of (opponent_score * result)
            # For simplicity, we'll just use Buchholz here
            sonneborn_berger = buchholz  # Simplified
            
            tiebreaks[user_id] = {
                "buchholz": buchholz,
                "sonneborn_berger": sonneborn_berger,
            }
        
        return tiebreaks
