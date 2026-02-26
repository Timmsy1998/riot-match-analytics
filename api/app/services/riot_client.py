from typing import Any
from urllib.parse import quote

import httpx


class RiotClient:
    BASE_URL_TEMPLATE = "https://{region}.api.riotgames.com"

    class RiotAPIError(Exception):
        def __init__(self, status_code: int, message: str) -> None:
            self.status_code = status_code
            self.message = message
            super().__init__(message)

    def __init__(self, api_key: str, region_routing: str) -> None:
        self.api_key = api_key
        self.base_url = self.BASE_URL_TEMPLATE.format(region=region_routing)

    async def get_match_ids_by_puuid(self, puuid: str, start: int = 0, count: int = 20) -> list[str]:
        endpoint = f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"start": start, "count": count}
        data = await self._get(endpoint=endpoint, params=params)

        if not isinstance(data, list):
            raise self.RiotAPIError(status_code=502, message="Unexpected Riot API response format.")

        return [str(match_id) for match_id in data]

    async def get_match(self, match_id: str) -> dict[str, Any]:
        endpoint = f"/lol/match/v5/matches/{match_id}"
        data = await self._get(endpoint=endpoint)

        if not isinstance(data, dict):
            raise self.RiotAPIError(status_code=502, message="Unexpected Riot API response format.")

        return data

    async def get_account_by_riot_id(self, game_name: str, tag_line: str) -> dict[str, Any]:
        encoded_game_name = quote(game_name, safe="")
        encoded_tag_line = quote(tag_line, safe="")
        endpoint = f"/riot/account/v1/accounts/by-riot-id/{encoded_game_name}/{encoded_tag_line}"
        data = await self._get(endpoint=endpoint)

        if not isinstance(data, dict):
            raise self.RiotAPIError(status_code=502, message="Unexpected Riot API response format.")

        return data

    async def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        headers = {"X-Riot-Token": self.api_key}
        timeout = httpx.Timeout(10.0)

        async with httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=timeout) as client:
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
