# Riot Match Analytics

A League of Legends analytics microservice built on the Riot API.

Created by **James Timms (Timmsy)**.

## Overview
This service ingests Riot match data and exposes practical analytics endpoints for player and match evaluation.

I built it as a backend-focused project to demonstrate:
- clear API design
- practical data transformation
- production-minded engineering choices
- test-first reliability with automated checks

## Why I Built It This Way
### 1) Riot ID first, not PUUID first
Most users do not know their PUUID, so public endpoints accept `game_name` and `tag_line`. The service resolves PUUID internally and keeps that complexity out of the client.

### 2) Separate routing domains in Riot API calls
Riot has both regional and platform routing concerns. Match/account style calls and league/summoner style calls are handled explicitly to reduce integration mistakes and make debugging easier.

### 3) Analytics logic separated from route handlers
Pure analytics functions live in services (`match_analytics.py`, `player_analytics.py`) so they can be tested independently of HTTP. This keeps route files thin and lowers regression risk.

### 4) Rate-limit aware behavior
Higher-cost endpoints such as summary and trend can trigger many Riot calls. Concurrency is constrained and 429 retry handling is implemented with `Retry-After` support.

### 5) Commit-time and CI testing
I wanted fast confidence while iterating, so tests run:
- locally via git hooks before commit
- in CI on push and pull request

## Stack
- Python 3.12
- FastAPI
- Uvicorn
- HTTPX
- Pytest
- Docker + Docker Compose

## Project Layout
```text
.
├── api/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   │   ├── match_summary.py
│   │   │   └── player_analytics.py
│   │   ├── routers/
│   │   │   ├── health.py
│   │   │   ├── matches.py
│   │   │   └── players.py
│   │   ├── services/
│   │   │   ├── match_analytics.py
│   │   │   ├── player_analytics.py
│   │   │   └── riot_client.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_health.py
│   │   ├── test_match_analytics.py
│   │   ├── test_matches_router.py
│   │   ├── test_player_analytics.py
│   │   └── test_players_router.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── .githooks/
├── .github/workflows/
├── scripts/
├── .env
├── .env.example
└── docker-compose.yml
```

## Configuration
Copy `.env.example` to `.env`.

Required variables:
- `RIOT_API_KEY`
- `RIOT_REGION_ROUTING` (example: `europe`)
- `RIOT_PLATFORM_ROUTING` (example: `euw1`)

App variables:
- `APP_ENV` (default: `development`)
- `APP_HOST` (default: `0.0.0.0`)
- `APP_PORT` (default: `8000`)

## Running the Service
### Docker (recommended)
```bash
docker compose up --build
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

### Local (without Docker)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements-dev.txt
cd api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing
### Run tests manually
```bash
docker compose run --rm riot-match-analytics-test
```

### Pre-commit test hook
```bash
./scripts/install-git-hooks.sh
```

This configures `.githooks/pre-commit` to run the Dockerized pytest suite before each commit.

### CI
Workflow file:
- `.github/workflows/test.yml`

CI installs dev dependencies and runs pytest for each push and pull request.

## API Endpoints
### Health
- `GET /health`

### Matches
- `GET /v1/matches/by-riot-id/{game_name}/{tag_line}?start=0&count=20`
- `GET /v1/matches/{match_id}`

### Players
- `GET /v1/players/by-riot-id/{game_name}/{tag_line}/profile`
- `GET /v1/players/by-riot-id/{game_name}/{tag_line}/summary?start=0&count=10`
- `GET /v1/players/by-riot-id/{game_name}/{tag_line}/performance-trend?start=0&count=10&recent_window=5`

## Current Scope
Implemented:
- Riot account resolution by Riot ID + tag
- Match retrieval and match summary analytics
- Player profile, summary, and trend analytics
- Ranked fallback lookup support (`by-puuid` then `by-summoner`)
- Automated tests and Docker-based workflow

Planned next:
- timeline analytics
- champion pool depth metrics
- caching layer for repeated profile/match queries
- auth/rate limiting for public deployment
