from pydantic import BaseModel


class RankedQueueEntry(BaseModel):
    queue_type: str
    tier: str
    rank: str
    league_points: int
    wins: int
    losses: int


class PlayerProfile(BaseModel):
    game_name: str
    tag_line: str
    puuid: str
    summoner_level: int
    ranked: list[RankedQueueEntry]


class ChampionPerformance(BaseModel):
    champion_name: str
    games: int
    wins: int
    win_rate: float
    avg_kda: float


class PlayerSummary(BaseModel):
    puuid: str
    games_analyzed: int
    win_rate: float
    avg_kda: float
    avg_cs_per_min: float
    avg_vision_score: float
    avg_gold_per_min: float
    top_champions: list[ChampionPerformance]


class PerformanceTrend(BaseModel):
    puuid: str
    games_analyzed: int
    win_rate_overall: float
    win_rate_recent: float
    avg_kda_overall: float
    avg_kda_recent: float
    kda_delta_recent_vs_overall: float
