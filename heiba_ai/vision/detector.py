from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import cv2
import numpy as np

@dataclass
class Detection:
    cls: str
    score: float
    bbox: tuple[int, int, int, int]
    source: str = "opencv-test-backend"

    def as_dict(self):
        return asdict(self)

class Detector:
    """Replaceable detector interface. The fallback is explicitly a test backend."""
    def __init__(self, model_path: Path | None = None, confidence: float = .35):
        self.model_path = model_path
        self.confidence = confidence
        self.model_name = "unverified-test-backend" if model_path is None else model_path.name
        self.net = None
        if model_path and model_path.exists():
            try:
                self.net = cv2.dnn.readNetFromONNX(str(model_path))
            except Exception:
                self.net = None

    def detect(self, frame: np.ndarray) -> list[Detection]:
        # Conservative motion/shape evidence for smoke tests only; no fabricated confidence.
        if frame is None or frame.size == 0:
            return []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 20, 35]), np.array([179, 255, 255]))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h, w = frame.shape[:2]
        out: list[Detection] = []
        for c in contours:
            x, y, bw, bh = cv2.boundingRect(c)
            area = bw * bh
            if area < max(80, w * h * .002) or area > w * h * .8:
                continue
            ratio = bw / max(bh, 1)
            cls = "ball" if .65 <= ratio <= 1.5 and area < w * h * .08 else "cup_or_barrel"
            score = min(.95, max(.35, area / (w * h * .15)))
            out.append(Detection(cls, float(score), (x, y, bw, bh)))
        return out[:30]
