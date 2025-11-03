from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import List

from .reports import format_event_overview
from .repository import TournamentRepository
from .scheduler import ScheduleRequest, build_round_robin
from .simulator import simulate_matches


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="tournament-ops-intelligence",
        description="Tournament Operations Intelligence Suite CLI",
    )
    parser.set_defaults(command=None)

    subparsers = parser.add_subparsers(dest="command")

    schedule_parser = subparsers.add_parser("schedule", help="Generate a round-robin schedule")
    schedule_parser.add_argument("input", type=Path, help="Path to event JSON")
    schedule_parser.add_argument("--stage", default="Group", help="Stage label to apply")
    schedule_parser.add_argument("--start", required=True, help="Start datetime (ISO format)")
    schedule_parser.add_argument("--match-duration", type=int, default=60, help="Match duration minutes")
    schedule_parser.add_argument("--matches-per-day", type=int, default=4, help="Matches per day")
    schedule_parser.add_argument("--best-of", type=int, default=3, help="Best-of value for matches")
    schedule_parser.add_argument("--venues", nargs="*", help="Optional list of venue ids to rotate through")
    schedule_parser.add_argument("--output", type=Path, help="Where to write updated event JSON")

    simulate_parser = subparsers.add_parser("simulate", help="Simulate match results")
    simulate_parser.add_argument("input", type=Path, help="Path to event JSON")
    simulate_parser.add_argument("--seed", type=int, help="Random seed for deterministic results")
    simulate_parser.add_argument("--output", type=Path, help="Where to write updated event JSON")

    report_parser = subparsers.add_parser("report", help="Print event report summary")
    report_parser.add_argument("input", type=Path, help="Path to event JSON")

    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command is None:
        raise SystemExit("No command selected. Use --help for options.")

    if args.command == "schedule":
        repo = TournamentRepository.from_json(args.input)
        request = ScheduleRequest(
            stage=args.stage,
            start_time=_parse_datetime(args.start),
            match_duration_minutes=args.match_duration,
            matches_per_day=args.matches_per_day,
            best_of=args.best_of,
            venue_ids=args.venues,
        )
        matches = build_round_robin(repo.event, request)
        repo.upsert_matches(matches)
        if args.output:
            repo.save_json(args.output)
        else:
            print(f"Generated {len(matches)} matches.")
        return 0

    if args.command == "simulate":
        repo = TournamentRepository.from_json(args.input)
        matches = simulate_matches(repo.event, seed=args.seed)
        repo.upsert_matches(matches)
        if args.output:
            repo.save_json(args.output)
        else:
            print("Simulation completed. Run the report command to view updated standings.")
        return 0

    if args.command == "report":
        repo = TournamentRepository.from_json(args.input)
        print(format_event_overview(repo.event))
        return 0

    raise SystemExit(f"Unknown command: {args.command}")


def _parse_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid datetime format: {value}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
