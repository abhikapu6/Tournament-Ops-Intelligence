# Tournament Operations Intelligence Suite

Operational toolkit for tournament directors, broadcast partners, and analytics
staff. The suite ships with core modules for:

- ingesting structured event data (teams, venues, matches)
- generating balanced round-robin schedules
- simulating match outcomes using roster ratings
- surfacing analytics such as standings, strength of schedule, and match highlights
- producing concise textual reports for briefings

The codebase is self-contained (standard library only) and includes a sample data
set plus unit tests.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Sample data

A ready-to-use event lives at `data/sample_event.json`. It models a four-team,
two-venue round robin called *Summer Showdown 2024*. Use it to explore scheduling,
simulation, and reporting flows.

## CLI usage

All commands expect `PYTHONPATH=src` when running from the repository root.

```bash
# Generate a round robin schedule starting July 1st at 09:00
PYTHONPATH=src python3 -m tournament_ops_intelligence.cli schedule \\
  data/sample_event.json \\
  --start 2024-07-01T09:00:00 \\
  --stage \"Group Stage\" \\
  --matches-per-day 3 \\
  --output data/scheduled_event.json

# Simulate results for the scheduled event (deterministic seed optional)
PYTHONPATH=src python3 -m tournament_ops_intelligence.cli simulate \\
  data/scheduled_event.json \\
  --seed 42 \\
  --output data/simulated_event.json

# Produce an operations report for briefs or broadcast prep
PYTHONPATH=src python3 -m tournament_ops_intelligence.cli report \\
  data/simulated_event.json
```

Key CLI arguments:

- `--start`: ISO timestamp for the first match slot (e.g. `2024-07-01T09:00:00`)
- `--matches-per-day`: caps block size before rolling to the next day
- `--venues`: optional list of venue IDs to rotate (defaults to all venues)
- `--best-of`: series length for scheduling and simulation

## Python modules

- `models.py`: dataclasses describing players, teams, venues, matches, and events
- `repository.py`: JSON ingest/emit helpers and in-memory repository
- `scheduler.py`: round-robin scheduler powered by the circle method
- `analytics.py`: standings, win probability, and strength-of-schedule metrics
- `simulator.py`: probabilistic series simulator based on roster ratings
- `reports.py`: formatted event overviews for quick consumption
- `cli.py`: argparse-driven entry point bundling the capabilities above

## Running tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Extending the suite

- Layer in persistence by swapping `TournamentRepository` for a database-backed
  implementation.
- Add alternative scheduling strategies (Swiss, double round robin).
- Enrich reports with broadcast windows, staffing requirements, or travel plans.
