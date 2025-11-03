from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List


@dataclass(slots=True)
class Player:
    """Represents a competitor participating in the event."""

    id: str
    name: str
    rating: float
    role: str = "player"
    status: str | None = None


@dataclass(slots=True)
class Team:
    """Team competing in the tournament."""

    id: str
    name: str
    players: List[Player]
    region: str | None = None
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def average_rating(self) -> float:
        """Average rating derived from listed players."""
        if not self.players:
            return 0.0
        return sum(player.rating for player in self.players) / len(self.players)


@dataclass(slots=True)
class Venue:
    """Physical or virtual location hosting a match."""

    id: str
    name: str
    capacity: int | None = None
    timezone: str = "UTC"
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class MatchResult:
    """Completed match details."""

    match_id: str
    winner_id: str
    team_one_score: int
    team_two_score: int
    concluded_at: datetime | None = None
    notes: str | None = None

    @property
    def is_tie(self) -> bool:
        return self.team_one_score == self.team_two_score


@dataclass(slots=True)
class Match:
    """Scheduled or completed match between two teams."""

    id: str
    stage: str
    round_number: int
    team_one_id: str
    team_two_id: str
    scheduled_time: datetime
    best_of: int = 1
    venue_id: str | None = None
    result: MatchResult | None = None

    def involves_team(self, team_id: str) -> bool:
        return team_id in {self.team_one_id, self.team_two_id}

    def has_result(self) -> bool:
        return self.result is not None


@dataclass(slots=True)
class Event:
    """Top-level container for tournament data."""

    id: str
    name: str
    start_date: date
    end_date: date
    teams: Dict[str, Team]
    venues: Dict[str, Venue]
    matches: List[Match]
    metadata: Dict[str, str] = field(default_factory=dict)

    def get_team(self, team_id: str) -> Team:
        return self.teams[team_id]

    def get_venue(self, venue_id: str) -> Venue:
        return self.venues[venue_id]

    def add_match(self, match: Match) -> None:
        self.matches.append(match)
