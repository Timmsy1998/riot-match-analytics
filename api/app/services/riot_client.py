from typing import Any
from urllib.parse import quote

import httpx


class RiotClient:
    REGION_BASE_URL_TEMPLATE = "https://{region}.api.riotgames.com"
    PLATFORM_BASE_URL_TEMPLATE = "https://{platform}.api.riotgames.com"

    class RiotAPIError(Exception):
        def __init__(self, status_code: int, message: str) -> None:
            self.status_code = status_code
            self.message = message
            super().__init__(message)

    def __init__(self, api_key: str, region_routing: str, platform_routing: str | None = None) -> None:
        self.api_key = api_key
        self.region_base_url = self.REGION_BASE_URL_TEMPLATE.format(region=region_routing)
        self.platform_base_url = None
        if platform_routing:
            self.platform_base_url = self.PLATFORM_BASE_URL_TEMPLATE.format(platform=platform_routing)

    async def get_match_ids_by_puuid(self, puuid: str, start: int = 0, count: int = 20) -> list[str]:
        endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"start": start, "count": count}
        data = await self._get_region(endpoint=endpoint, params=params)

        if not isinstance(data, list):
            raise self.RiotAPIError(status_code=502, message="Unexpected Riot API response format.")

        return [str(match_id) for match_id in data]

    async def get_match(self, match_id: str) -> dict[str, Any]:
        endpoint = f"/lol/match/v5/matches/{match_id}"
        data = await self._get_region(endpoint=endpoint)

        if not isinstance(data, dict):
            raise self.RiotAPIError(status_code=502, message="Unexpected Riot API response format.")

        return data

    async def get_account_by_riot_id(self, game_name: str, tag_line: str) -> dict[str, Any]:
        encoded_game_name = quote(game_name, safe="")
        encoded_tag_line = quote(tag_line, safe="")
        endpoint = f"/riot/account/v1/accounts/by-riot-id/{encoded_game_name}/{encoded_tag_line}"
        data = await self._get_region(endpoint=endpoint)

        if not isinstance(data, dict):
            raise self.RiotAPIError(status_code=502, message="Unexpected Riot API response format.")

        return data

    async def get_summoner_by_puuid(self, puuid: str) -> dict[str, Any]:
        endpoint = f"/lol/summoner/v4/summoners/by-puuid/{quote(puuid, safe='')}"
        data = await self._get_platform(endpoint=endpoint)

        if not isinstance(data, dict):
            raise self.RiotAPIError(status_code=502, message="Unexpected Riot API response format.")

        return data

    async def get_league_entries_by_summoner(self, encrypted_summoner_id: str) -> list[dict[str, Any]]:
        endpoint = f"/lol/league/v4/entries/by-summoner/{quote(encrypted_summoner_id, safe='')}"
        data = await self._get_platform(endpoint=endpoint)

        if not isinstance(data, list):
            raise self.RiotAPIError(status_code=502, message="Unexpected Riot API response format.")

        entries: list[dict[str, Any]] = []
        for item in data:
            if isinstance(item, dict):
                entries.append(item)
        return entries

    async def _get_region(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        return await self._get(base_url=self.region_base_url, endpoint=endpoint, params=params)

    async def _get_platform(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        if not self.platform_base_url:
            raise self.RiotAPIError(
                status_code=500,
                message="RIOT_PLATFORM_ROUTING is required for this endpoint.",
            )
        return await self._get(base_url=self.platform_base_url, endpoint=endpoint, params=params)

    async def _get(self, base_url: str, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        headers = {"X-Riot-Token": self.api_key}
        timeout = httpx.Timeout(10.0)

        async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=timeout) as client:
            response = await client.get(endpoint, params=params)

        if response.status_code >= 400:
            message = self._message_for_error(response.status_code)
            raise self.RiotAPIError(status_code=response.status_code, message=message)

        return response.json()

    @staticmethod
    def _message_for_error(status_code: int) -> str:
        messages = {
            400: "Bad request to Riot API.",
            401: "Unauthorized. Check your Riot API key.",
            403: "Forbidden access to Riot API endpoint.",
            404: "Resource not found in Riot API.",
            429: "Rate limit exceeded by Riot API.",
            500: "Riot API internal server error.",
            503: "Riot API is temporarily unavailable.",
        }
        return messages.get(status_code, "Unexpected error from Riot API.")
