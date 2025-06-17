"""Entry point for Neuropuppet training and live control."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from core.utils import load_config, setup_logger
from core.control import MotorController
from core.vision import PoseTracker
from core.rl_agent import PuppetEnv, train_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Neuropuppet")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--train", action="store_true", help="Run PPO training")
    parser.add_argument("--timesteps", type=int, help="Override training steps")
    parser.add_argument("--sequence", help="Run movement sequence from YAML")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    log = setup_logger()
    serial_cfg = cfg.get("serial", {})
    vision_cfg = cfg.get("vision", {})
    rl_cfg = cfg.get("rl", {})

    controller = MotorController(
        port=serial_cfg.get("port", "/dev/ttyACM0"),
        baudrate=int(serial_cfg.get("baudrate", 115200)),
        timeout=float(serial_cfg.get("timeout", 1.0)),
    )

    if args.sequence:
        from core.sequence import load_sequence, play_sequence
        sequence = load_sequence(args.sequence)
        try:
            play_sequence(controller, sequence)
        finally:
            controller.close()
        return

    tracker = PoseTracker(
        camera_index=int(vision_cfg.get("camera_index", 0)),
        use_mediapipe=bool(vision_cfg.get("use_mediapipe", True)),
    )

    env = PuppetEnv(controller, tracker)

    try:
        if args.train:
            total_steps = int(args.timesteps or rl_cfg.get("total_timesteps", 10000))
            train_agent(env, total_timesteps=total_steps,
                        learning_rate=float(rl_cfg.get("learning_rate", 3e-4)),
                        device=str(rl_cfg.get("device", "cpu")))
        else:
            log.info("Starting live control loop. Press Ctrl+C to exit.")
            while True:
                obs, _ = env.reset()
                log.info("Observed keypoints: %s", obs)
    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        env.close()


if __name__ == "__main__":
    main()
