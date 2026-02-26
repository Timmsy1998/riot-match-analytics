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
│   │   │   └── matches.py
│   │   ├── services/
│   │   │   └── riot_client.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_health.py
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
source .venv/bin/activate
cd api
pytest -q
```

## Initial Endpoints
- `GET /health`
- `GET /v1/matches/by-puuid/{puuid}?start=0&count=20`
- `GET /v1/matches/by-riot-id/{game_name}/{tag_line}?start=0&count=20`
- `GET /v1/matches/{match_id}` (returns raw Riot match + analytics summary)
