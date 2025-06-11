"""Vision module for Neuropuppet.

Uses OpenCV/MediaPipe to extract 2D keypoints of the puppet.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

import cv2
try:
    import mediapipe as mp
except ImportError:  # pragma: no cover - optional dependency
    mp = None

from .utils import setup_logger


@dataclass
class Keypoints:
    points: Dict[str, Tuple[int, int]]


class PoseTracker:
    """Track puppet pose using MediaPipe or basic color blob detection."""

    def __init__(self, camera_index: int = 0, use_mediapipe: bool = True) -> None:
        self.log = setup_logger(self.__class__.__name__)
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            self.log.error("Cannot open camera %s", camera_index)
            raise RuntimeError("Camera not available")
        self.use_mediapipe = use_mediapipe and mp is not None
        if self.use_mediapipe:
            self.pose = mp.solutions.pose.Pose()
            self.log.info("Using MediaPipe for pose tracking")
        else:
            self.pose = None
            self.log.info("Using simple color tracking")

    def read_frame(self) -> Keypoints | None:
        ret, frame = self.cap.read()
        if not ret:
            self.log.warning("Failed to read frame")
            return None
        if self.use_mediapipe and self.pose:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb)
            if not results.pose_landmarks:
                return None
            h, w, _ = frame.shape
            pts = {
                "left_hand": (int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST].x * w),
                               int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_WRIST].y * h)),
                "right_hand": (int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_WRIST].x * w),
                                int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_WRIST].y * h)),
                "left_foot": (int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ANKLE].x * w),
                               int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ANKLE].y * h)),
                "right_foot": (int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE].x * w),
                                int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE].y * h)),
                "head": (int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE].x * w),
                         int(results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE].y * h)),
            }
            return Keypoints(points=pts)
        # Basic placeholder: return center of image as all points
        h, w, _ = frame.shape
        center = (w // 2, h // 2)
        return Keypoints(points={"center": center})

    def close(self) -> None:
        if self.cap:
            self.cap.release()
        if self.pose:
            self.pose.close()
        cv2.destroyAllWindows()
