"""Base agent definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BaseAgent:
    """Simple base class for all IPO analysis agents."""

    name: str

    def run(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement the run method.")
