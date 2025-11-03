from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Sequence

from .models import Event, Match


@dataclass(slots=True)
class ScheduleRequest:
    stage: str
    start_time: datetime
    match_duration_minutes: int = 60
    matches_per_day: int = 4
    best_of: int = 3
    venue_ids: Sequence[str] | None = None


def build_round_robin(event: Event, request: ScheduleRequest) -> List[Match]:
    """
    Generate a round-robin schedule for the provided event.

    The algorithm uses the standard circle method, producing home/away neutral pairings.
    """
    team_ids = sorted(event.teams.keys())
    if len(team_ids) < 2:
        return []

    venues = list(request.venue_ids) if request.venue_ids else list(event.venues.keys())
    if not venues:
        venues = [None]  # type: ignore[list-item]

    match_duration = timedelta(minutes=request.match_duration_minutes)
    matches_per_day = max(1, request.matches_per_day)

    schedule: List[Match] = []
    current_time = request.start_time
    matches_scheduled_today = 0
    match_counter = 1

    for round_number, pairings in enumerate(_generate_round_robin_pairings(team_ids), start=1):
        for team_one_id, team_two_id in pairings:
            if team_two_id is None:
                continue  # bye week
            venue_id = venues[(match_counter - 1) % len(venues)]
            match_id = f"{request.stage.lower().replace(' ', '-')}-r{round_number:02d}-m{match_counter:03d}"
            schedule.append(
                Match(
                    id=match_id,
                    stage=request.stage,
                    round_number=round_number,
                    team_one_id=team_one_id,
                    team_two_id=team_two_id,
                    scheduled_time=current_time,
                    best_of=request.best_of,
                    venue_id=venue_id,
                )
            )
            matches_scheduled_today += 1
            match_counter += 1

            if matches_scheduled_today >= matches_per_day:
                current_time = _advance_to_next_day(request.start_time, current_time)
                matches_scheduled_today = 0
            else:
                current_time += match_duration

    return schedule


def _generate_round_robin_pairings(team_ids: Sequence[str]) -> Iterable[List[tuple[str, str | None]]]:
    """Yield pairings for each round using the circle method."""
    teams = list(team_ids)
    has_bye = len(teams) % 2 == 1
    if has_bye:
        teams.append("BYE")

    num_rounds = len(teams) - 1
    half = len(teams) // 2

    for _ in range(num_rounds):
        round_pairings: List[tuple[str, str | None]] = []
        for i in range(half):
            team_one = teams[i]
            team_two = teams[-i - 1]
            if "BYE" in (team_one, team_two):
                if team_one == "BYE":
                    round_pairings.append((team_two, None))
                else:
                    round_pairings.append((team_one, None))
            else:
                round_pairings.append((team_one, team_two))
        yield round_pairings
        teams = [teams[0]] + teams[-1:] + teams[1:-1]


def _advance_to_next_day(start_time: datetime, current_time: datetime) -> datetime:
    next_day = current_time + timedelta(days=1)
    return next_day.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second, microsecond=start_time.microsecond)

