from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

from .models import Event, Match


@dataclass(slots=True)
class TeamPerformance:
    team_id: str
    matches_played: int = 0
    wins: int = 0
    losses: int = 0
    ties: int = 0
    maps_won: int = 0
    maps_lost: int = 0

    @property
    def map_difference(self) -> int:
        return self.maps_won - self.maps_lost

    @property
    def win_rate(self) -> float:
        return self.wins / self.matches_played if self.matches_played else 0.0


def compute_standings(event: Event, matches: Iterable[Match] | None = None) -> List[TeamPerformance]:
    matches = list(matches) if matches is not None else event.matches
    performances: Dict[str, TeamPerformance] = {
        team_id: TeamPerformance(team_id=team_id) for team_id in event.teams.keys()
    }

    for match in matches:
        if match.result is None:
            continue
        perf_one = performances[match.team_one_id]
        perf_two = performances[match.team_two_id]
        perf_one.matches_played += 1
        perf_two.matches_played += 1
        perf_one.maps_won += match.result.team_one_score
        perf_one.maps_lost += match.result.team_two_score
        perf_two.maps_won += match.result.team_two_score
        perf_two.maps_lost += match.result.team_one_score

        if match.result.team_one_score == match.result.team_two_score:
            perf_one.ties += 1
            perf_two.ties += 1
        elif match.result.winner_id == match.team_one_id:
            perf_one.wins += 1
            perf_two.losses += 1
        else:
            perf_two.wins += 1
            perf_one.losses += 1

    return sorted(
        performances.values(),
        key=lambda perf: (perf.wins, perf.map_difference, perf.maps_won),
        reverse=True,
    )


def expected_score(event: Event, team_one_id: str, team_two_id: str) -> Tuple[float, float]:
    team_one = event.teams[team_one_id]
    team_two = event.teams[team_two_id]
    elo_one = team_one.average_rating
    elo_two = team_two.average_rating
    exp_one = 1 / (1 + math.pow(10, (elo_two - elo_one) / 400))
    exp_two = 1 - exp_one
    return exp_one, exp_two


def suggest_highlight_matches(event: Event, threshold: float = 0.1) -> List[Match]:
    """
    Return matches predicted to be close (probabilities within threshold of 0.5).
    Useful for broadcast priority decisions.
    """
    highlights: List[Match] = []
    for match in event.matches:
        prob_one, prob_two = expected_score(event, match.team_one_id, match.team_two_id)
        if abs(prob_one - prob_two) <= threshold:
            highlights.append(match)
    return highlights


def strength_of_schedule(event: Event) -> Dict[str, float]:
    """Average opponent rating for each team based on scheduled matches."""
    sos: Dict[str, List[float]] = {team_id: [] for team_id in event.teams.keys()}
    for match in event.matches:
        sos[match.team_one_id].append(event.teams[match.team_two_id].average_rating)
        sos[match.team_two_id].append(event.teams[match.team_one_id].average_rating)
    return {
        team_id: (sum(values) / len(values)) if values else 0.0
        for team_id, values in sos.items()
    }

