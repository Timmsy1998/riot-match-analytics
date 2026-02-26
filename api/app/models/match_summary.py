from pydantic import BaseModel


class TeamSummary(BaseModel):
    team_id: int
    win: bool
    total_kills: int
    total_deaths: int
    total_assists: int


class TopPerformerSummary(BaseModel):
    puuid: str
    champion_name: str
    kda_ratio: float
    kills: int
    deaths: int
    assists: int


class MatchSummary(BaseModel):
    match_id: str
    game_mode: str
    game_duration_seconds: int
    teams: list[TeamSummary]
    top_performer: TopPerformerSummary | None
