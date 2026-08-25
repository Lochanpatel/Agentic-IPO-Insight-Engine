"""Application configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Simple configuration used by the IPO analysis engine."""

    project_root: Path
    default_ticker: str = "EXMP"
    default_company_name: str = "Example IPO"
    environment: str = "development"


def get_settings() -> Settings:
    root = Path(__file__).resolve().parents[2]
    return Settings(
        project_root=root,
        default_ticker=os.getenv("DEFAULT_TICKER", "EXMP"),
        default_company_name=os.getenv("DEFAULT_COMPANY_NAME", "Example IPO"),
        environment=os.getenv("ENVIRONMENT", "development"),
    )
