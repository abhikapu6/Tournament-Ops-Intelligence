import unittest
from datetime import datetime
from pathlib import Path

from tournament_ops_intelligence.repository import TournamentRepository
from tournament_ops_intelligence.scheduler import ScheduleRequest, build_round_robin


class SchedulerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = TournamentRepository.from_json(Path("data/sample_event.json"))

    def test_round_robin_generates_unique_pairings(self) -> None:
        start = datetime.fromisoformat("2024-07-01T09:00:00")
        request = ScheduleRequest(
            stage="Groups",
            start_time=start,
            match_duration_minutes=45,
            matches_per_day=3,
            best_of=1,
        )
        matches = build_round_robin(self.repo.event, request)
        self.assertEqual(len(matches), 6)  # 4 teams -> 6 matches
        seen_pairs = set()
        for match in matches:
            pair = tuple(sorted([match.team_one_id, match.team_two_id]))
            self.assertNotIn(pair, seen_pairs)
            seen_pairs.add(pair)
        self.assertEqual(len(seen_pairs), 6)


if __name__ == "__main__":
    unittest.main()
