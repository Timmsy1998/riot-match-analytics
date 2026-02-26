# riot-match-analytics

Riot API Match Analytics Microservice for League of Legends.

## Tech Stack
- Python 3.12
- FastAPI
- Uvicorn
- HTTPX
- Docker + Docker Compose

## Project Structure
```text
.
├── api/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py
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
├── .env
├── .env.example
└── docker-compose.yml
```

## Environment Variables
Copy `.env.example` to `.env` and set values.

- `RIOT_API_KEY`: Riot developer API key
- `RIOT_REGION_ROUTING`: Regional routing value (`europe`, `americas`, `asia`, `sea`)
- `RIOT_PLATFORM_ROUTING`: Platform routing value (`euw1`, `na1`, etc.)
- `APP_ENV`: Environment name (`development` by default)
- `APP_HOST`: Host binding (`0.0.0.0` by default)
- `APP_PORT`: Port (`8000` by default)

## Run with Docker
From repo root:

```bash
docker compose up --build
```

Service URL:
- `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

## Run Locally (without Docker)
From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements-dev.txt
cd api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run Tests
From repo root:

```bash
docker compose run --rm riot-match-analytics-test
```

## Git Test Workflow
### Local (before every commit)
Install the repo git hooks once:

```bash
./scripts/install-git-hooks.sh
```

This enables `.githooks/pre-commit`, which runs `pytest -q` before each commit.
The hook runs tests inside Docker using `docker compose run --rm riot-match-analytics-test`.

### CI (on push and pull request)
GitHub Actions workflow is defined in:
- `.github/workflows/test.yml`

It installs `api/requirements-dev.txt` and runs `pytest -q`.

## Initial Endpoints
- `GET /health`
- `GET /v1/matches/by-puuid/{puuid}?start=0&count=20`
- `GET /v1/matches/by-riot-id/{game_name}/{tag_line}?start=0&count=20`
- `GET /v1/matches/{match_id}` (returns raw Riot match + analytics summary)
- `GET /v1/players/by-riot-id/{game_name}/{tag_line}/profile`
- `GET /v1/players/{puuid}/summary?start=0&count=20`
- `GET /v1/players/{puuid}/performance-trend?start=0&count=20&recent_window=5`
