"""Application configuration helpers."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    """Configuration for IPO analysis engine.
    
    Settings can be overridden via environment variables:
    - DEFAULT_TICKER: Stock ticker symbol (default: "EXMP")
    - DEFAULT_COMPANY_NAME: Company name (default: "Example IPO")
    - ENVIRONMENT: Deployment environment (default: "development")
    - LOG_LEVEL: Logging level (default: "INFO")
    """

    project_root: Path
    default_ticker: str = "EXMP"
    default_company_name: str = "Example IPO"
    environment: str = "development"
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        """Validate settings after initialization."""
        if not self.project_root.exists():
            logger.warning(f"Project root does not exist: {self.project_root}")
        
        if not self.default_ticker or len(self.default_ticker) > 5:
            logger.warning(f"Invalid default ticker: {self.default_ticker}")
        
        if self.environment not in ("development", "staging", "production"):
            logger.warning(f"Unknown environment: {self.environment}")
        
        logger.info(f"Settings initialized: {self.environment} mode, ticker={self.default_ticker}")

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    def get_data_dir(self) -> Path:
        """Get the data directory path."""
        data_dir = self.project_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    def get_logs_dir(self) -> Path:
        """Get the logs directory path."""
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir


def get_settings() -> Settings:
    """Load application settings from environment and defaults.
    
    Returns:
        Settings object with configuration
    """
    root = Path(__file__).resolve().parents[2]
    
    settings = Settings(
        project_root=root,
        default_ticker=os.getenv("DEFAULT_TICKER", "EXMP"),
        default_company_name=os.getenv("DEFAULT_COMPANY_NAME", "Example IPO"),
        environment=os.getenv("ENVIRONMENT", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
    
    logger.debug(f"Settings loaded from environment")
    return settings


def configure_logging(log_level: str | None = None) -> None:
    """Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    settings = get_settings()
    level = log_level or settings.log_level
    
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ],
    )
    
    logger.info(f"Logging configured at {level} level")
