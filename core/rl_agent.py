"""Reinforcement learning environment and agent for Neuropuppet."""
from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

import gymnasium as gym
import numpy as np
import cv2
from stable_baselines3 import PPO

from .control import MotorController
from .vision import PoseTracker, Keypoints
from .utils import setup_logger


class PuppetEnv(gym.Env):
    """Custom Gym environment for puppet control."""

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, controller: MotorController, tracker: PoseTracker) -> None:
        super().__init__()
        self.log = setup_logger(self.__class__.__name__)
        self.controller = controller
        self.tracker = tracker
        # Observation: 5 keypoints with (x, y) coordinates normalized to [0,1]
        self.observation_space = gym.spaces.Box(low=0.0, high=1.0, shape=(10,))
        # Action: relative steps for 6 motors in range [-1,1]
        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(6,))

    def _get_obs(self) -> np.ndarray:
        keypoints = self.tracker.read_frame()
        if keypoints is None:
            return np.zeros(self.observation_space.shape)
        h, w = self.tracker.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.tracker.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        pts = keypoints.points
        # If using center-only placeholder
        if "center" in pts:
            c = pts["center"]
            return np.array([c[0]/w, c[1]/h] * 5, dtype=np.float32)
        order = ["left_hand", "right_hand", "left_foot", "right_foot", "head"]
        obs = []
        for name in order:
            x, y = pts.get(name, (0, 0))
            obs.extend([x / w, y / h])
        return np.array(obs, dtype=np.float32)

    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        obs = self._get_obs()
        return obs, {}

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        # Convert actions to motor steps
        step_scale = 100  # placeholder scaling factor
        for i, val in enumerate(action):
            steps = int(val * step_scale)
            self.controller.move_motor(i + 1, steps)
        obs = self._get_obs()
        # Placeholder reward: keep center near middle of frame
        center_x, center_y = obs[-2], obs[-1]
        reward = 1.0 - ((center_x - 0.5) ** 2 + (center_y - 0.5) ** 2)
        terminated = False
        truncated = False
        info: Dict[str, Any] = {}
        return obs, reward, terminated, truncated, info

    def render(self) -> None:
        pass

    def close(self) -> None:
        self.tracker.close()
        self.controller.close()


def train_agent(env: PuppetEnv, total_timesteps: int = 10000, learning_rate: float = 3e-4, device: str = "cpu") -> PPO:
    log = setup_logger("Trainer")
    model = PPO("MlpPolicy", env, verbose=1, learning_rate=learning_rate, device=device)
    log.info("Starting PPO training for %d steps", total_timesteps)
    model.learn(total_timesteps=total_timesteps)
    log.info("Training complete")
    return model
