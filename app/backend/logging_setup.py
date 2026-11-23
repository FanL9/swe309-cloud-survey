"""Logging: always to stdout (collected by cloud platforms), optionally to a file.

Comments are never logged, and no IP addresses are recorded, to keep
personal data out of the logs (PDPA).
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER_NAME = "survey"
FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def setup_logging(config):
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(config["LOG_LEVEL"])
    logger.propagate = False
    for handler in list(logger.handlers):  # create_app may run more than once (tests)
        handler.close()
        logger.removeHandler(handler)

    formatter = logging.Formatter(FORMAT)
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    if config["LOG_FILE"]:
        path = Path(config["LOG_FILE"])
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            path, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
