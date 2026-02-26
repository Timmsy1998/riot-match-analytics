from typing import Any

from app.models.player_analytics import ChampionPerformance, PerformanceTrend, PlayerSummary


def build_player_summary(puuid: str, matches: list[dict[str, Any]]) -> PlayerSummary:
    participants = [_find_participant_for_puuid(match, puuid) for match in matches]
    participants = [p for p in participants if p is not None]

    games = len(participants)
    if games == 0:
        return PlayerSummary(
            puuid=puuid,
            games_analyzed=0,
            win_rate=0.0,
            avg_kda=0.0,
            avg_cs_per_min=0.0,
            avg_vision_score=0.0,
            avg_gold_per_min=0.0,
            top_champions=[],
        )

    wins = sum(1 for p in participants if bool(p.get("win", False)))
    avg_kda = _round2(sum(_kda(p) for p in participants) / games)

    cs_per_min_values = [_cs_per_min(match, p) for match, p in zip(matches, participants)]
    gold_per_min_values = [_gold_per_min(match, p) for match, p in zip(matches, participants)]

    top_champions = _build_top_champions(participants)

    return PlayerSummary(
        puuid=puuid,
        games_analyzed=games,
        win_rate=_round2((wins / games) * 100),
        avg_kda=avg_kda,
        avg_cs_per_min=_round2(sum(cs_per_min_values) / games),
        avg_vision_score=_round2(sum(float(p.get("visionScore", 0)) for p in participants) / games),
        avg_gold_per_min=_round2(sum(gold_per_min_values) / games),
        top_champions=top_champions,
    )


def build_performance_trend(puuid: str, matches: list[dict[str, Any]], recent_window: int = 5) -> PerformanceTrend:
    participants = [_find_participant_for_puuid(match, puuid) for match in matches]
    participants = [p for p in participants if p is not None]

    games = len(participants)
    if games == 0:
        return PerformanceTrend(
            puuid=puuid,
            games_analyzed=0,
            win_rate_overall=0.0,
            win_rate_recent=0.0,
            avg_kda_overall=0.0,
            avg_kda_recent=0.0,
            kda_delta_recent_vs_overall=0.0,
        )

    recent_participants = participants[-recent_window:]

    overall_win_rate = _round2((sum(1 for p in participants if bool(p.get("win", False))) / games) * 100)
    recent_win_rate = _round2(
        (sum(1 for p in recent_participants if bool(p.get("win", False))) / len(recent_participants)) * 100
    )

    avg_kda_overall = _round2(sum(_kda(p) for p in participants) / games)
    avg_kda_recent = _round2(sum(_kda(p) for p in recent_participants) / len(recent_participants))

    return PerformanceTrend(
        puuid=puuid,
        games_analyzed=games,
        win_rate_overall=overall_win_rate,
        win_rate_recent=recent_win_rate,
        avg_kda_overall=avg_kda_overall,
        avg_kda_recent=avg_kda_recent,
        kda_delta_recent_vs_overall=_round2(avg_kda_recent - avg_kda_overall),
    )


def _find_participant_for_puuid(match: dict[str, Any], puuid: str) -> dict[str, Any] | None:
    participants = match.get("info", {}).get("participants", [])
    for participant in participants:
        if str(participant.get("puuid", "")) == puuid:
            return participant
    return None


def _kda(participant: dict[str, Any]) -> float:
    kills = int(participant.get("kills", 0))
    assists = int(participant.get("assists", 0))
    deaths = int(participant.get("deaths", 0))
    return (kills + assists) / max(1, deaths)


def _cs_per_min(match: dict[str, Any], participant: dict[str, Any]) -> float:
    duration_seconds = int(match.get("info", {}).get("gameDuration", 0))
    duration_minutes = max(1.0, duration_seconds / 60)
    cs = int(participant.get("totalMinionsKilled", 0)) + int(participant.get("neutralMinionsKilled", 0))
    return cs / duration_minutes


def _gold_per_min(match: dict[str, Any], participant: dict[str, Any]) -> float:
    duration_seconds = int(match.get("info", {}).get("gameDuration", 0))
    duration_minutes = max(1.0, duration_seconds / 60)
    gold = int(participant.get("goldEarned", 0))
    return gold / duration_minutes


def _build_top_champions(participants: list[dict[str, Any]]) -> list[ChampionPerformance]:
    by_champion: dict[str, list[dict[str, Any]]] = {}
    for p in participants:
        champion = str(p.get("championName", "Unknown"))
        by_champion.setdefault(champion, []).append(p)

    champion_rows: list[ChampionPerformance] = []
    for champion, rows in by_champion.items():
        games = len(rows)
        wins = sum(1 for row in rows if bool(row.get("win", False)))
        avg_kda = _round2(sum(_kda(row) for row in rows) / games)
        champion_rows.append(
            ChampionPerformance(
                champion_name=champion,
                games=games,
                wins=wins,
                win_rate=_round2((wins / games) * 100),
                avg_kda=avg_kda,
            )
        )

    champion_rows.sort(key=lambda c: (c.games, c.win_rate, c.avg_kda), reverse=True)
    return champion_rows[:3]


def _round2(value: float) -> float:
    return round(value, 2)
