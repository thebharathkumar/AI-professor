"""
Logging configuration
"""
import logging
import sys
from pathlib import Path
from config import settings


def setup_logging(log_file: str = None) -> None:
    """
    Configure logging for the application

    Args:
        log_file: Optional path to log file
    """
    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    # Reduce noise from some libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('anthropic').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
