"""Main application entry point with all features wired"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.config import settings
from app.database import init_db, close_db

# Routers
from app.routers import auth, users, games, puzzles, tournaments
from app.routers import leaderboard, board_themes, offline, analysis, challenges

# WebSocket routers
from app.websockets.game_socket import router as game_ws_router
from app.websockets.matchmaking_socket import router as matchmaking_ws_router
from app.websockets.ai_game_socket import router as ai_game_ws_router

# Middleware
from app.middleware.rate_limiter import RateLimiterMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized")
    
    # Initialize clock ticker
    from app.websockets.game_state import game_manager
    from app.websockets.connection_manager import manager
    
    # Set broadcast callback for the ticker
    game_manager.set_broadcast_callback(manager.broadcast_to_game)
    await game_manager.start_ticker()
    logger.info("Clock ticker started")
    
    yield
    # Shutdown
    logger.info("Stopping clock ticker...")
    await game_manager.stop_ticker()
    
    logger.info("Closing database...")
    await close_db()
    logger.info("Database closed")


app = FastAPI(
    title="Chess Platform API",
    description="A comprehensive chess platform with real-time multiplayer, puzzles, tournaments, AI play, analysis, and more",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# --- Middleware ---

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter
app.add_middleware(RateLimiterMiddleware)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing"""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code} ({duration:.3f}s)"
    )
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions and return a safe 500 response"""
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# --- API Routers ---
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(games.router, prefix="/api/games", tags=["Games"])
app.include_router(puzzles.router, prefix="/api/puzzles", tags=["Puzzles"])
app.include_router(tournaments.router, prefix="/api/tournaments", tags=["Tournaments"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["Leaderboard"])
app.include_router(board_themes.router, prefix="/api/board-themes", tags=["Board Themes"])
app.include_router(offline.router, prefix="/api/offline", tags=["Offline"])
app.include_router(analysis.router, prefix="/api/games", tags=["Analysis"])
app.include_router(challenges.router, prefix="/api/challenges", tags=["Challenges"])

# --- WebSocket Routers ---
app.include_router(game_ws_router, tags=["Game WebSocket"])
app.include_router(matchmaking_ws_router, tags=["Matchmaking WebSocket"])
app.include_router(ai_game_ws_router, tags=["AI Game WebSocket"])


# --- Health check ---
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": [
            "multiplayer",
            "puzzles",
            "tournaments",
            "ai_play",
            "analysis",
            "leaderboard",
            "challenges",
            "spectator_mode",
            "offline_mode",
            "board_themes",
        ],
    }
