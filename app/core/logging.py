"""Logging configuration."""

import logging


def configure_logging(level: str) -> None:
    """Configure process logging once, with a useful integration format."""

    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
