"""Logging configuration module for structured application-wide logs."""

import logging


def setup_logging(verbose: bool = False) -> None:
    """Configure application-wide logging format and severity level.

    Args:
        verbose: If True, set root log level to DEBUG; otherwise INFO.
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
