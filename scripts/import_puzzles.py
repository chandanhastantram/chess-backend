"""Puzzle data importer for Lichess puzzle CSV format"""
import asyncio
import csv
import sys
import os
from typing import List

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session_maker, init_db
from app.models.puzzle import Puzzle


async def import_puzzles(csv_path: str, limit: int = 1000):
    """
    Import puzzles from a Lichess-formatted CSV file.
    
    Expected format: PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags
    """
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found.")
        return

    print(f"Starting import from {csv_path}...")
    
    count = 0
    async with async_session_maker() as session:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip header if it exists
            header = next(reader)
            if header[0] != "PuzzleId":
                # Not a header, or at least not the one we expect, so re-handle
                f.seek(0)
            
            for row in reader:
                if count >= limit:
                    break
                
                try:
                    # Parse row
                    puzzle_id_str = row[0]
                    fen = row[1]
                    moves = row[2].split(' ')
                    rating = int(row[3])
                    popularity = int(row[5])
                    themes = row[7].split(' ')
                    
                    puzzle = Puzzle(
                        fen=fen,
                        moves=moves,
                        rating=rating,
                        popularity=popularity,
                        themes=themes
                    )
                    
                    session.add(puzzle)
                    count += 1
                    
                    if count % 100 == 0:
                        await session.commit()
                        print(f"Imported {count} puzzles...")
                        
                except Exception as e:
                    print(f"Error skipping row {count}: {e}")
                    continue
        
        await session.commit()
        print(f"Import complete. Total: {count}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import puzzles from Lichess CSV")
    parser.add_argument("csv_path", help="Path to the Lichess puzzles CSV file")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum number of puzzles to import")
    
    args = parser.parse_args()
    
    asyncio.run(import_puzzles(args.csv_path, args.limit))
