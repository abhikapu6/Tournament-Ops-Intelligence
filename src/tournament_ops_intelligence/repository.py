from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, List

from .models import Event, Match, MatchResult, Player, Team, Venue


def _parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover - close error message
        raise ValueError(f"Invalid datetime format: {value}") from exc


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:  # pragma: no cover
        raise ValueError(f"Invalid date format: {value}") from exc


class TournamentRepository:
    """Loads and stores tournament data."""

    def __init__(self, event: Event):
        self._event = event

    @property
    def event(self) -> Event:
        return self._event

    @classmethod
    def from_json(cls, path: Path | str) -> "TournamentRepository":
        raw_data = json.loads(Path(path).read_text())
        event = _event_from_dict(raw_data)
        return cls(event)

    def to_dict(self) -> dict:
        return _event_to_dict(self._event)

    def list_teams(self) -> Iterable[Team]:
        return self._event.teams.values()

    def list_matches(self) -> Iterable[Match]:
        return list(self._event.matches)

    def list_venues(self) -> Iterable[Venue]:
        return self._event.venues.values()

    def upsert_matches(self, matches: Iterable[Match]) -> None:
        """Replace matches with the same id or append new ones."""
        matches_by_id = {match.id: match for match in matches}
        existing = {match.id: match for match in self._event.matches}
        existing.update(matches_by_id)
        self._event.matches = list(sorted(existing.values(), key=lambda m: (m.stage, m.round_number, m.scheduled_time)))

    def record_results(self, results: Iterable[MatchResult]) -> None:
        matches_by_id = {match.id: match for match in self._event.matches}
        for result in results:
            match = matches_by_id.get(result.match_id)
            if match is None:
                continue
            match.result = result

    def save_json(self, path: Path | str) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True))


def _event_from_dict(payload: dict) -> Event:
    event_meta = payload["event"]
    teams = {}
    for team_data in payload.get("teams", []):
        players = [
            Player(
                id=player["id"],
                name=player["name"],
                rating=float(player.get("rating", 0)),
                role=player.get("role", "player"),
                status=player.get("status"),
            )
            for player in team_data.get("players", [])
        ]
        teams[team_data["id"]] = Team(
            id=team_data["id"],
            name=team_data["name"],
            players=players,
            region=team_data.get("region"),
            metadata=team_data.get("metadata", {}),
        )

    venues = {
        venue_data["id"]: Venue(
            id=venue_data["id"],
            name=venue_data["name"],
            capacity=venue_data.get("capacity"),
            timezone=venue_data.get("timezone", "UTC"),
            metadata=venue_data.get("metadata", {}),
        )
        for venue_data in payload.get("venues", [])
    }

    matches: List[Match] = []
    for match_data in payload.get("matches", []):
        result: MatchResult | None = None
        if "result" in match_data and match_data["result"] is not None:
            res_payload = match_data["result"]
            result = MatchResult(
                match_id=match_data["id"],
                winner_id=res_payload["winner_id"],
                team_one_score=int(res_payload["team_one_score"]),
                team_two_score=int(res_payload["team_two_score"]),
                concluded_at=_parse_datetime(res_payload["concluded_at"]) if res_payload.get("concluded_at") else None,
                notes=res_payload.get("notes"),
            )
        matches.append(
            Match(
                id=match_data["id"],
                stage=match_data.get("stage", "Main"),
                round_number=int(match_data.get("round_number", 1)),
                team_one_id=match_data["team_one_id"],
                team_two_id=match_data["team_two_id"],
                scheduled_time=_parse_datetime(match_data["scheduled_time"]),
                best_of=int(match_data.get("best_of", 1)),
                venue_id=match_data.get("venue_id"),
                result=result,
            )
        )

    return Event(
        id=event_meta["id"],
        name=event_meta["name"],
        start_date=_parse_date(event_meta["start_date"]),
        end_date=_parse_date(event_meta["end_date"]),
        teams=teams,
        venues=venues,
        matches=matches,
        metadata=payload.get("metadata", {}),
    )


def _event_to_dict(event: Event) -> dict:
    return {
        "event": {
            "id": event.id,
            "name": event.name,
            "start_date": event.start_date.isoformat(),
            "end_date": event.end_date.isoformat(),
        },
        "metadata": event.metadata,
        "teams": [
            {
                "id": team.id,
                "name": team.name,
                "region": team.region,
                "metadata": team.metadata,
                "players": [
                    {
                        "id": player.id,
                        "name": player.name,
                        "rating": player.rating,
                        "role": player.role,
                        "status": player.status,
                    }
                    for player in team.players
                ],
            }
            for team in event.teams.values()
        ],
        "venues": [
            {
                "id": venue.id,
                "name": venue.name,
                "capacity": venue.capacity,
                "timezone": venue.timezone,
                "metadata": venue.metadata,
            }
            for venue in event.venues.values()
        ],
        "matches": [
            {
                "id": match.id,
                "stage": match.stage,
                "round_number": match.round_number,
                "team_one_id": match.team_one_id,
                "team_two_id": match.team_two_id,
                "scheduled_time": match.scheduled_time.isoformat(),
                "best_of": match.best_of,
                "venue_id": match.venue_id,
            "result": None
            if match.result is None
            else {
                "match_id": match.result.match_id,
                "winner_id": match.result.winner_id,
                "team_one_score": match.result.team_one_score,
                "team_two_score": match.result.team_two_score,
                "concluded_at": match.result.concluded_at.isoformat()
                if match.result.concluded_at
                    else None,
                    "notes": match.result.notes,
                },
            }
            for match in event.matches
        ],
    }
