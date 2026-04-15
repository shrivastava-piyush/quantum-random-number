"""Execution telemetry helpers."""

from __future__ import annotations

import logging
import sys

_CONFIGURED = False


def get_logger(name: str = "qrng", level: str | int = "INFO") -> logging.Logger:
    """Return a lazily-configured logger writing to stderr.

    Stdout is reserved for random bytes when piping through the CLI; all
    telemetry therefore lives on stderr.
    """
    global _CONFIGURED
    logger = logging.getLogger(name)
    if not _CONFIGURED:
        handler = logging.StreamHandler(stream=sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
        )
        root = logging.getLogger("qrng")
        root.addHandler(handler)
        root.propagate = False
        _CONFIGURED = True
    logger.setLevel(level)
    return logger
