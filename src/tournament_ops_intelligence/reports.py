from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from .analytics import TeamPerformance, compute_standings, suggest_highlight_matches
from .models import Event, Match


def format_event_overview(event: Event, matches: Iterable[Match] | None = None) -> str:
    matches = list(matches) if matches is not None else event.matches
    standings = compute_standings(event, matches)
    highlights = suggest_highlight_matches(event)

    report_lines: List[str] = []
    report_lines.append(f"Event: {event.name} ({event.start_date} to {event.end_date})")
    report_lines.append(f"Teams ({len(event.teams)} total):")
    for team in sorted(event.teams.values(), key=lambda t: t.name):
        report_lines.append(f"  - {team.name} [{team.id}] | Avg Rating: {team.average_rating:.1f}")

    report_lines.append("")
    report_lines.append("Upcoming Schedule:")
    future_matches = [m for m in matches if m.scheduled_time >= datetime.utcnow()]
    for match in future_matches[:10]:
        report_lines.append(
            f"  {match.scheduled_time.isoformat()} | {event.teams[match.team_one_id].name} vs {event.teams[match.team_two_id].name} "
            f"(Stage: {match.stage}, Round: {match.round_number})"
        )
    if not future_matches:
        report_lines.append("  No remaining scheduled matches.")

    report_lines.append("")
    report_lines.append("Standings:")
    if any(perf.matches_played for perf in standings):
        report_lines.extend(_format_standings_table(event, standings))
    else:
        report_lines.append("  No completed matches yet.")

    if highlights:
        report_lines.append("")
        report_lines.append("Predicted Close Matchups:")
        for match in highlights[:5]:
            report_lines.append(
                f"  {event.teams[match.team_one_id].name} vs {event.teams[match.team_two_id].name} "
                f"on {match.scheduled_time.date()} (Stage {match.stage})"
            )

    return "\n".join(report_lines)


def _format_standings_table(event: Event, standings: List[TeamPerformance]) -> List[str]:
    rows = [
        "  Team                          W   L   T   Maps   Win%"
    ]
    for perf in standings:
        team_name = event.teams[perf.team_id].name
        rows.append(
            f"  {team_name:<28} {perf.wins:>2}  {perf.losses:>2}  {perf.ties:>2}  "
            f"{perf.map_difference:>+3}   {perf.win_rate*100:5.1f}"
        )
    return rows

