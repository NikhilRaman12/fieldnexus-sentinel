# utilis.py
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def get_logger(
    name: str = "fieldnexus",
    log_dir: str = "logs",
    log_file: str = "pipeline.log"
) -> logging.Logger:
    """
    Configure and return a logger that writes to both console and file.
    Ensures consistent formatting across the pipeline.
    """
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(os.path.join(log_dir, log_file), encoding="utf-8")
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def ensure_dir(path: str) -> None:
    """Ensure that a directory exists."""
    os.makedirs(path, exist_ok=True)


def save_json(obj: Dict[str, Any], path: str) -> None:
    """Save a dictionary as a JSON file."""
    ensure_dir(os)