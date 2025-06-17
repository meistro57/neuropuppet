from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .control import MotorController
from .utils import setup_logger


def load_sequence(path: str | Path) -> List[Dict[str, Any]]:
    """Load a movement sequence from a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError("Sequence YAML must be a list of steps")
    return data


def play_sequence(controller: MotorController, sequence: List[Dict[str, Any]]) -> None:
    """Execute a sequence of motor steps."""
    log = setup_logger("SequencePlayer")
    for step in sequence:
        motor = int(step.get("motor", 0))
        steps = int(step.get("steps", 0))
        delay = float(step.get("delay", 0))
        log.info("Motor %d -> %d steps (delay %.2fs)", motor, steps, delay)
        controller.move_motor(motor, steps)
        if delay > 0:
            time.sleep(delay)
