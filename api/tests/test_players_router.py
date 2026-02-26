from fastapi.testclient import TestClient

from app.main import app
from app.services.riot_client import RiotClient


def _fake_match(match_id: str, puuid: str) -> dict:
    return {
        "metadata": {"matchId": match_id},
        "info": {
            "gameDuration": 1800,
            "participants": [
                {
                    "puuid": puuid,
                    "championName": "Ahri",
                    "win": True,
                    "kills": 6,
                    "deaths": 2,
                    "assists": 7,
                    "totalMinionsKilled": 200,
                    "neutralMinionsKilled": 20,
                    "visionScore": 30,
                    "goldEarned": 13000,
                }
            ],
        },
    }


def test_profile_by_riot_id_success(monkeypatch) -> None:
    monkeypatch.setenv("RIOT_API_KEY", "test-key")
    monkeypatch.setenv("RIOT_REGION_ROUTING", "europe")
    monkeypatch.setenv("RIOT_PLATFORM_ROUTING", "euw1")

    async def fake_get_account_by_riot_id(self, game_name: str, tag_line: str):
        return {"puuid": "puuid-1", "gameName": game_name, "tagLine": tag_line}

    async def fake_get_summoner_by_puuid(self, puuid: str):
        return {"id": "summoner-enc-1", "summonerLevel": 420}

    async def fake_get_league_entries_by_summoner(self, encrypted_summoner_id: str):
        return [
            {
                "queueType": "RANKED_SOLO_5x5",
                "tier": "GOLD",
                "rank": "II",
                "leaguePoints": 75,
                "wins": 40,
                "losses": 35,
            }
        ]

    monkeypatch.setattr(RiotClient, "get_account_by_riot_id", fake_get_account_by_riot_id)
    monkeypatch.setattr(RiotClient, "get_summoner_by_puuid", fake_get_summoner_by_puuid)
    monkeypatch.setattr(RiotClient, "get_league_entries_by_summoner", fake_get_league_entries_by_summoner)

    client = TestClient(app)
    response = client.get("/v1/players/by-riot-id/ash%20timmy/%23EUW/profile")

    assert response.status_code == 200
    payload = response.json()
    assert payload["puuid"] == "puuid-1"
    assert payload["summoner_level"] == 420
    assert payload["ranked"][0]["queue_type"] == "RANKED_SOLO_5x5"


def test_player_summary_success(monkeypatch) -> None:
    monkeypatch.setenv("RIOT_API_KEY", "test-key")

    async def fake_get_match_ids_by_puuid(self, puuid: str, start: int, count: int):
        return ["EUW1_1", "EUW1_2"]

    async def fake_get_match(self, match_id: str):
        return _fake_match(match_id, puuid="puuid-1")

    monkeypatch.setattr(RiotClient, "get_match_ids_by_puuid", fake_get_match_ids_by_puuid)
    monkeypatch.setattr(RiotClient, "get_match", fake_get_match)

    client = TestClient(app)
    response = client.get("/v1/players/puuid-1/summary?count=2")

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["games_analyzed"] == 2
    assert payload["summary"]["puuid"] == "puuid-1"


def test_player_trend_success(monkeypatch) -> None:
    monkeypatch.setenv("RIOT_API_KEY", "test-key")

    async def fake_get_match_ids_by_puuid(self, puuid: str, start: int, count: int):
        return ["EUW1_1", "EUW1_2", "EUW1_3", "EUW1_4", "EUW1_5"]

    async def fake_get_match(self, match_id: str):
        return _fake_match(match_id, puuid="puuid-1")

    monkeypatch.setattr(RiotClient, "get_match_ids_by_puuid", fake_get_match_ids_by_puuid)
    monkeypatch.setattr(RiotClient, "get_match", fake_get_match)

    client = TestClient(app)
    response = client.get("/v1/players/puuid-1/performance-trend?count=5&recent_window=3")

    assert response.status_code == 200
    payload = response.json()
    assert payload["trend"]["games_analyzed"] == 5
    assert payload["trend"]["puuid"] == "puuid-1"
