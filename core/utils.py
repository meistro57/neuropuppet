"""Utility functions for Neuropuppet.

Provides configuration loading and a simple logger setup.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import yaml


def setup_logger(name: str = "neuropuppet", level: int = logging.INFO) -> logging.Logger:
    """Configure and return a module-level logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def load_config(path: str | Path) -> Dict[str, Any]:
    """Load YAML configuration from ``path``."""
    with open(path, "r", encoding="utf-8") as f:
        cfg: Dict[str, Any] = yaml.safe_load(f)
    return cfg
