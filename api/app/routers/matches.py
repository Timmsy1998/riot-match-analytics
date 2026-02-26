from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.models.match_summary import MatchSummary
from app.services.match_analytics import build_match_summary
from app.services.riot_client import RiotClient

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("/by-puuid/{puuid}")
async def get_recent_matches_by_puuid(
    puuid: str,
    start: int = Query(default=0, ge=0),
    count: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if not settings.riot_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RIOT_API_KEY is not configured.",
        )

    client = RiotClient(
        api_key=settings.riot_api_key,
        region_routing=settings.riot_region_routing,
    )

    try:
        matches = await client.get_match_ids_by_puuid(puuid=puuid, start=start, count=count)
    except RiotClient.RiotAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return {
        "puuid": puuid,
        "region": settings.riot_region_routing,
        "start": start,
        "count": count,
        "matches": matches,
    }


@router.get("/by-riot-id/{game_name}/{tag_line}")
async def get_recent_matches_by_riot_id(
    game_name: str,
    tag_line: str,
    start: int = Query(default=0, ge=0),
    count: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if not settings.riot_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RIOT_API_KEY is not configured.",
        )

    normalized_tag_line = tag_line.lstrip("#")
    client = RiotClient(
        api_key=settings.riot_api_key,
        region_routing=settings.riot_region_routing,
    )

    try:
        account = await client.get_account_by_riot_id(game_name=game_name, tag_line=normalized_tag_line)
        puuid = str(account.get("puuid", ""))
        if not puuid:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Riot account response did not include a puuid.",
            )
        matches = await client.get_match_ids_by_puuid(puuid=puuid, start=start, count=count)
    except RiotClient.RiotAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return {
        "game_name": str(account.get("gameName", game_name)),
        "tag_line": str(account.get("tagLine", normalized_tag_line)),
        "puuid": puuid,
        "region": settings.riot_region_routing,
        "start": start,
        "count": count,
        "matches": matches,
    }


@router.get("/{match_id}")
async def get_match_with_summary(
    match_id: str,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if not settings.riot_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RIOT_API_KEY is not configured.",
        )

    client = RiotClient(
        api_key=settings.riot_api_key,
        region_routing=settings.riot_region_routing,
    )

    try:
        match_data = await client.get_match(match_id=match_id)
    except RiotClient.RiotAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    summary: MatchSummary = build_match_summary(match_data)
    return {
        "match_id": match_id,
        "region": settings.riot_region_routing,
        "summary": summary.model_dump(),
        "match": match_data,
    }
