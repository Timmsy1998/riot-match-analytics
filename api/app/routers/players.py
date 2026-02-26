import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.models.player_analytics import PlayerProfile, RankedQueueEntry
from app.services.player_analytics import build_performance_trend, build_player_summary
from app.services.riot_client import RiotClient

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/by-riot-id/{game_name}/{tag_line}/profile")
async def get_player_profile_by_riot_id(
    game_name: str,
    tag_line: str,
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    client = _build_client_or_raise(settings)
    normalized_tag_line = tag_line.lstrip("#")

    try:
        account = await client.get_account_by_riot_id(game_name=game_name, tag_line=normalized_tag_line)
        puuid = str(account.get("puuid", ""))
        if not puuid:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Riot account response did not include a puuid.",
            )

        summoner = await client.get_summoner_by_puuid(puuid=puuid)
        summoner_id = str(summoner.get("id", ""))
        ranked_entries = []
        if summoner_id:
            ranked_entries = await client.get_league_entries_by_summoner(encrypted_summoner_id=summoner_id)
    except RiotClient.RiotAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    profile = PlayerProfile(
        game_name=str(account.get("gameName", game_name)),
        tag_line=str(account.get("tagLine", normalized_tag_line)),
        puuid=puuid,
        summoner_level=int(summoner.get("summonerLevel", 0)),
        ranked=[
            RankedQueueEntry(
                queue_type=str(entry.get("queueType", "")),
                tier=str(entry.get("tier", "")),
                rank=str(entry.get("rank", "")),
                league_points=int(entry.get("leaguePoints", 0)),
                wins=int(entry.get("wins", 0)),
                losses=int(entry.get("losses", 0)),
            )
            for entry in ranked_entries
        ],
    )

    return profile.model_dump()


@router.get("/{puuid}/summary")
async def get_player_summary(
    puuid: str,
    start: int = Query(default=0, ge=0),
    count: int = Query(default=20, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    client = _build_client_or_raise(settings)

    try:
        match_ids = await client.get_match_ids_by_puuid(puuid=puuid, start=start, count=count)
        matches = await _load_matches(client=client, match_ids=match_ids)
    except RiotClient.RiotAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    summary = build_player_summary(puuid=puuid, matches=matches)
    return {
        "region": settings.riot_region_routing,
        "start": start,
        "count": count,
        "summary": summary.model_dump(),
    }


@router.get("/{puuid}/performance-trend")
async def get_player_performance_trend(
    puuid: str,
    start: int = Query(default=0, ge=0),
    count: int = Query(default=20, ge=5, le=50),
    recent_window: int = Query(default=5, ge=3, le=10),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    client = _build_client_or_raise(settings)

    try:
        match_ids = await client.get_match_ids_by_puuid(puuid=puuid, start=start, count=count)
        matches = await _load_matches(client=client, match_ids=match_ids)
    except RiotClient.RiotAPIError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    trend = build_performance_trend(puuid=puuid, matches=matches, recent_window=recent_window)
    return {
        "region": settings.riot_region_routing,
        "start": start,
        "count": count,
        "recent_window": recent_window,
        "trend": trend.model_dump(),
    }


def _build_client_or_raise(settings: Settings) -> RiotClient:
    if not settings.riot_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="RIOT_API_KEY is not configured.",
        )

    return RiotClient(
        api_key=settings.riot_api_key,
        region_routing=settings.riot_region_routing,
        platform_routing=settings.riot_platform_routing,
    )


async def _load_matches(client: RiotClient, match_ids: list[str]) -> list[dict[str, Any]]:
    if not match_ids:
        return []

    tasks = [client.get_match(match_id) for match_id in match_ids]
    return await asyncio.gather(*tasks)
