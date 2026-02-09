# Chess Backend

A production-grade chess platform backend with high availability, replicating chess.com's functionality.

## Features

- ✅ Real-time multiplayer chess with WebSockets
- ✅ Stockfish AI opponent integration
- ✅ Glicko-2 rating system
- ✅ Advanced tournament systems (Swiss, Round-Robin)
- ✅ Puzzle system
- ✅ User authentication and profiles
- ✅ High availability architecture (no single points of failure)

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with async SQLAlchemy
- **Message Broker**: RabbitMQ
- **Chess Engine**: python-chess + Stockfish
- **Authentication**: JWT tokens
- **Deployment**: Kubernetes with Patroni for database HA

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Stockfish chess engine
- RabbitMQ (for production)

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd chess
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database:

```bash
# Create PostgreSQL database
createdb chess_db

# Run migrations (after setting up Alembic)
alembic upgrade head
```

### Running the Application

**Development mode:**

```bash
uvicorn app.main:app --reload
```

**Production mode with Gunicorn:**

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
chess/
├── app/
│   ├── models/          # Database models
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   ├── middleware/      # Middleware
│   ├── utils/           # Utilities
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   ├── schemas.py       # Pydantic schemas
│   └── main.py          # FastAPI app
├── tests/               # Tests
├── kubernetes/          # K8s manifests
├── requirements.txt
└── README.md
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Games (Coming soon)

- `POST /api/games/create` - Create new game
- `POST /api/games/{game_id}/move` - Make a move
- `GET /api/games/{game_id}` - Get game details

### Tournaments (Coming soon)

- `GET /api/tournaments` - List tournaments
- `POST /api/tournaments` - Create tournament
- `POST /api/tournaments/{id}/join` - Join tournament

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint
flake8 app/

# Type checking
mypy app/
```

## Production Deployment

See [implementation_plan.md](implementation_plan.md) for detailed production deployment guide with Kubernetes, PostgreSQL HA, and monitoring setup.

## License

MIT
