from app.services.player_analytics import build_performance_trend, build_player_summary


def _match(
    match_id: str,
    puuid: str,
    champion: str,
    win: bool,
    kills: int,
    deaths: int,
    assists: int,
    duration: int = 1800,
    cs: int = 180,
    neutral_cs: int = 30,
    vision_score: int = 20,
    gold_earned: int = 12000,
) -> dict:
    return {
        "metadata": {"matchId": match_id},
        "info": {
            "gameDuration": duration,
            "participants": [
                {
                    "puuid": puuid,
                    "championName": champion,
                    "win": win,
                    "kills": kills,
                    "deaths": deaths,
                    "assists": assists,
                    "totalMinionsKilled": cs,
                    "neutralMinionsKilled": neutral_cs,
                    "visionScore": vision_score,
                    "goldEarned": gold_earned,
                }
            ],
        },
    }


def test_build_player_summary() -> None:
    puuid = "p-1"
    matches = [
        _match("M1", puuid, "Ahri", True, 10, 2, 8),
        _match("M2", puuid, "Ahri", False, 5, 5, 4),
        _match("M3", puuid, "Lux", True, 7, 1, 12),
    ]

    summary = build_player_summary(puuid=puuid, matches=matches)

    assert summary.puuid == puuid
    assert summary.games_analyzed == 3
    assert summary.win_rate == 66.67
    assert summary.avg_kda > 0
    assert len(summary.top_champions) == 2
    assert summary.top_champions[0].champion_name == "Ahri"


def test_build_performance_trend() -> None:
    puuid = "p-1"
    matches = [
        _match("M1", puuid, "Ahri", False, 1, 8, 3),
        _match("M2", puuid, "Ahri", False, 2, 7, 4),
        _match("M3", puuid, "Ahri", True, 8, 2, 10),
        _match("M4", puuid, "Lux", True, 10, 1, 12),
        _match("M5", puuid, "Lux", True, 9, 2, 8),
    ]

    trend = build_performance_trend(puuid=puuid, matches=matches, recent_window=3)

    assert trend.puuid == puuid
    assert trend.games_analyzed == 5
    assert trend.win_rate_recent > trend.win_rate_overall
    assert trend.avg_kda_recent > trend.avg_kda_overall
    assert trend.kda_delta_recent_vs_overall > 0
