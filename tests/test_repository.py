import unittest
from pathlib import Path

from tournament_ops_intelligence.repository import TournamentRepository


class RepositoryTests(unittest.TestCase):
    def test_loads_sample_event(self) -> None:
        repo = TournamentRepository.from_json(Path("data/sample_event.json"))
        self.assertEqual(repo.event.name, "Summer Showdown 2024")
        self.assertEqual(len(repo.event.teams), 4)
        self.assertEqual(len(repo.event.venues), 2)


if __name__ == "__main__":
    unittest.main()
