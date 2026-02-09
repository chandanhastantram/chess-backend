"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db, close_db
from app.routers import auth, users, games, puzzles, tournaments
from app.websockets import game_router, matchmaking_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    print("🚀 Starting Chess Backend API...")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Chess Backend API...")
    await close_db()
    print("✅ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Chess Backend API",
    description="""
    Production-grade chess platform backend with high availability.
    
    ## Features
    - Real-time multiplayer chess with WebSockets
    - Stockfish AI opponent
    - Glicko-2 rating system
    - Swiss & Round-Robin tournaments
    - Puzzle system
    - User authentication & profiles
    - Friends & social features
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(games.router, prefix="/api/games", tags=["Games"])
app.include_router(puzzles.router, prefix="/api/puzzles", tags=["Puzzles"])
app.include_router(tournaments.router, prefix="/api/tournaments", tags=["Tournaments"])

# Include WebSocket routers
app.include_router(game_router, tags=["WebSocket - Game"])
app.include_router(matchmaking_router, tags=["WebSocket - Matchmaking"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Chess Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/stats")
async def api_stats():
    """Get API statistics"""
    from app.websockets.connection_manager import manager
    from app.websockets.game_state import game_manager
    from app.services.matchmaking import matchmaking_service
    
    return {
        "connected_users": manager.get_user_count(),
        "active_games": len(game_manager.games),
        "matchmaking_queues": matchmaking_service.get_queue_stats(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
