from typing import Any

from app.models.match_summary import MatchSummary, TeamSummary, TopPerformerSummary


def build_match_summary(match_data: dict[str, Any]) -> MatchSummary:
    metadata = match_data.get("metadata", {})
    info = match_data.get("info", {})

    participants = info.get("participants", [])
    teams = info.get("teams", [])

    team_summaries: list[TeamSummary] = []
    for team in teams:
        team_id = int(team.get("teamId", 0))
        team_participants = [p for p in participants if int(p.get("teamId", -1)) == team_id]

        team_summaries.append(
            TeamSummary(
                team_id=team_id,
                win=bool(team.get("win", False)),
                total_kills=sum(int(p.get("kills", 0)) for p in team_participants),
                total_deaths=sum(int(p.get("deaths", 0)) for p in team_participants),
                total_assists=sum(int(p.get("assists", 0)) for p in team_participants),
            )
        )

    top_performer = _get_top_performer(participants)

    return MatchSummary(
        match_id=str(metadata.get("matchId", "unknown")),
        game_mode=str(info.get("gameMode", "unknown")),
        game_duration_seconds=int(info.get("gameDuration", 0)),
        teams=team_summaries,
        top_performer=top_performer,
    )


def _get_top_performer(participants: list[dict[str, Any]]) -> TopPerformerSummary | None:
    if not participants:
        return None

    def participant_kda(p: dict[str, Any]) -> float:
        kills = int(p.get("kills", 0))
        assists = int(p.get("assists", 0))
        deaths = int(p.get("deaths", 0))
        return (kills + assists) / max(1, deaths)

    best = max(participants, key=participant_kda)
    kills = int(best.get("kills", 0))
    deaths = int(best.get("deaths", 0))
    assists = int(best.get("assists", 0))

    return TopPerformerSummary(
        puuid=str(best.get("puuid", "")),
        champion_name=str(best.get("championName", "Unknown")),
        kda_ratio=round((kills + assists) / max(1, deaths), 2),
        kills=kills,
        deaths=deaths,
        assists=assists,
    )
