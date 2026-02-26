from app.services.match_analytics import build_match_summary


def test_build_match_summary() -> None:
    match_data = {
        "metadata": {"matchId": "EUW1_12345"},
        "info": {
            "gameMode": "CLASSIC",
            "gameDuration": 1800,
            "teams": [
                {"teamId": 100, "win": True},
                {"teamId": 200, "win": False},
            ],
            "participants": [
                {
                    "puuid": "p1",
                    "teamId": 100,
                    "championName": "Ahri",
                    "kills": 10,
                    "deaths": 2,
                    "assists": 8,
                },
                {
                    "puuid": "p2",
                    "teamId": 100,
                    "championName": "LeeSin",
                    "kills": 3,
                    "deaths": 4,
                    "assists": 9,
                },
                {
                    "puuid": "p3",
                    "teamId": 200,
                    "championName": "Lux",
                    "kills": 2,
                    "deaths": 7,
                    "assists": 5,
                },
            ],
        },
    }

    summary = build_match_summary(match_data)

    assert summary.match_id == "EUW1_12345"
    assert summary.game_mode == "CLASSIC"
    assert summary.game_duration_seconds == 1800

    assert len(summary.teams) == 2
    team_100 = next(t for t in summary.teams if t.team_id == 100)
    team_200 = next(t for t in summary.teams if t.team_id == 200)

    assert team_100.total_kills == 13
    assert team_100.total_deaths == 6
    assert team_100.total_assists == 17
    assert team_100.win is True

    assert team_200.total_kills == 2
    assert team_200.total_deaths == 7
    assert team_200.total_assists == 5
    assert team_200.win is False

    assert summary.top_performer is not None
    assert summary.top_performer.puuid == "p1"
    assert summary.top_performer.champion_name == "Ahri"
    assert summary.top_performer.kda_ratio == 9.0
