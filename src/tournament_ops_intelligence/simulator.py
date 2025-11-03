from __future__ import annotations

import random
from dataclasses import replace
from datetime import timedelta
from typing import Iterable, List, Sequence

from .analytics import expected_score
from .models import Event, Match, MatchResult


def simulate_matches(event: Event, matches: Iterable[Match] | None = None, seed: int | None = None) -> List[Match]:
    """
    Generate simulated results for scheduled matches.

    The simulation uses a probabilistic model derived from average player ratings.
    """
    rng = random.Random(seed)
    scheduled_matches = list(matches) if matches is not None else list(event.matches)
    simulated: List[Match] = []
    for match in scheduled_matches:
        if match.result is not None:
            simulated.append(match)
            continue
        win_probability, _ = expected_score(event, match.team_one_id, match.team_two_id)
        team_one_wins, team_two_wins = _play_series(match.best_of, win_probability, rng)
        if team_one_wins == team_two_wins:
            # For best-of-one ties we record as draw; otherwise assign final game.
            if match.best_of == 1:
                winner_id = match.team_one_id if rng.random() < 0.5 else match.team_two_id
            else:
                winner_id = match.team_one_id if rng.random() < 0.5 else match.team_two_id
                if winner_id == match.team_one_id:
                    team_one_wins += 1
                else:
                    team_two_wins += 1
        else:
            winner_id = match.team_one_id if team_one_wins > team_two_wins else match.team_two_id

        result = MatchResult(
            match_id=match.id,
            winner_id=winner_id,
            team_one_score=team_one_wins,
            team_two_score=team_two_wins,
            concluded_at=match.scheduled_time + timedelta(minutes=45 * match.best_of),
        )
        simulated.append(replace(match, result=result))
    return simulated


def _play_series(best_of: int, win_probability: float, rng: random.Random) -> tuple[int, int]:
    required_wins = best_of // 2 + 1
    wins_one = 0
    wins_two = 0
    while wins_one < required_wins and wins_two < required_wins:
        if rng.random() < win_probability:
            wins_one += 1
        else:
            wins_two += 1
    return wins_one, wins_two

