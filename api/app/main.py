from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.matches import router as matches_router

app = FastAPI(
    title="Riot Match Analytics Microservice",
    version="0.1.0",
    description="Microservice for fetching and analyzing League of Legends match data.",
)

app.include_router(health_router)
app.include_router(matches_router, prefix="/v1")
