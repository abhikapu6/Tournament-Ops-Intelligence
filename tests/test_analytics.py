import unittest
from datetime import datetime
from pathlib import Path

from tournament_ops_intelligence.analytics import compute_standings, strength_of_schedule
from tournament_ops_intelligence.models import MatchResult
from tournament_ops_intelligence.repository import TournamentRepository
from tournament_ops_intelligence.scheduler import ScheduleRequest, build_round_robin


class AnalyticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = TournamentRepository.from_json(Path("data/sample_event.json"))
        request = ScheduleRequest(
            stage="Groups",
            start_time=datetime.fromisoformat("2024-07-01T09:00:00"),
            match_duration_minutes=60,
            matches_per_day=3,
            best_of=1,
        )
        matches = build_round_robin(self.repo.event, request)
        # Inject simple deterministic results
        for index, match in enumerate(matches):
            if index % 2 == 0:
                winner = match.team_one_id
                match.result = MatchResult(
                    match_id=match.id,
                    winner_id=winner,
                    team_one_score=1,
                    team_two_score=0,
                )
            else:
                winner = match.team_two_id
                match.result = MatchResult(
                    match_id=match.id,
                    winner_id=winner,
                    team_one_score=0,
                    team_two_score=1,
                )
        self.matches = matches

    def test_compute_standings_orders_by_wins(self) -> None:
        standings = compute_standings(self.repo.event, self.matches)
        wins = [perf.wins for perf in standings]
        self.assertTrue(all(wins[i] >= wins[i + 1] for i in range(len(wins) - 1)))

    def test_strength_of_schedule_returns_all_teams(self) -> None:
        sos = strength_of_schedule(self.repo.event)
        self.assertSetEqual(set(sos.keys()), set(self.repo.event.teams.keys()))


if __name__ == "__main__":
    unittest.main()
