from fastapi.testclient import TestClient

from app.main import app
from app.services.riot_client import RiotClient


class _DummyRiotError(RiotClient.RiotAPIError):
    pass


def test_get_matches_by_riot_id_success(monkeypatch) -> None:
    monkeypatch.setenv("RIOT_API_KEY", "test-key")
    monkeypatch.setenv("RIOT_REGION_ROUTING", "europe")

    async def fake_get_account_by_riot_id(self, game_name: str, tag_line: str):
        assert game_name == "ash timmy"
        assert tag_line == "ash"
        return {"puuid": "puuid-123", "gameName": game_name, "tagLine": tag_line}

    async def fake_get_match_ids_by_puuid(self, puuid: str, start: int, count: int):
        assert puuid == "puuid-123"
        assert start == 0
        assert count == 20
        return ["EUW1_1", "EUW1_2"]

    monkeypatch.setattr(RiotClient, "get_account_by_riot_id", fake_get_account_by_riot_id)
    monkeypatch.setattr(RiotClient, "get_match_ids_by_puuid", fake_get_match_ids_by_puuid)

    client = TestClient(app)
    response = client.get("/v1/matches/by-riot-id/ash%20timmy/%23ash")

    assert response.status_code == 200
    payload = response.json()
    assert payload["puuid"] == "puuid-123"
    assert payload["game_name"] == "ash timmy"
    assert payload["tag_line"] == "ash"
    assert payload["matches"] == ["EUW1_1", "EUW1_2"]


def test_get_match_with_summary_success(monkeypatch) -> None:
    monkeypatch.setenv("RIOT_API_KEY", "test-key")

    async def fake_get_match(self, match_id: str):
        return {
            "metadata": {"matchId": match_id},
            "info": {
                "gameMode": "CLASSIC",
                "gameDuration": 1200,
                "teams": [{"teamId": 100, "win": True}],
                "participants": [
                    {
                        "puuid": "p1",
                        "teamId": 100,
                        "championName": "Ahri",
                        "kills": 5,
                        "deaths": 1,
                        "assists": 4,
                    }
                ],
            },
        }

    monkeypatch.setattr(RiotClient, "get_match", fake_get_match)

    client = TestClient(app)
    response = client.get("/v1/matches/EUW1_999")

    assert response.status_code == 200
    payload = response.json()
    assert payload["match_id"] == "EUW1_999"
    assert payload["summary"]["match_id"] == "EUW1_999"
    assert payload["summary"]["top_performer"]["puuid"] == "p1"


def test_get_matches_by_riot_id_propagates_riot_errors(monkeypatch) -> None:
    monkeypatch.setenv("RIOT_API_KEY", "test-key")

    async def fake_get_account_by_riot_id(self, game_name: str, tag_line: str):
        raise _DummyRiotError(status_code=404, message="Resource not found in Riot API.")

    monkeypatch.setattr(RiotClient, "get_account_by_riot_id", fake_get_account_by_riot_id)

    client = TestClient(app)
    response = client.get("/v1/matches/by-riot-id/missing/user")

    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found in Riot API."
