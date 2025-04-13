import logging
from logging.handlers import RotatingFileHandler
import sys
from typing import Optional


class Logger:
    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(
        cls, name: str = "app", log_file: Optional[str] = None, level=logging.INFO
    ) -> logging.Logger:
        if cls._instance:
            return cls._instance

        logger = logging.getLogger(name)
        logger.setLevel(level)

        if logger.hasHandlers():
            cls._instance = logger
            return logger

        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=5_000_000, backupCount=3
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._instance = logger
        return logger
