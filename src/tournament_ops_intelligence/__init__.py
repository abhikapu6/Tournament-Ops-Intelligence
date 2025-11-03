"""
Tournament Operations Intelligence Suite.

This package provides scheduling, analytics, simulation, and reporting utilities
for managing competitive tournaments.
"""

from .models import Event, Match, Player, Team, Venue
from .repository import TournamentRepository

__all__ = [
    "Event",
    "Match",
    "Player",
    "Team",
    "Venue",
    "TournamentRepository",
]

__version__ = "0.1.0"
