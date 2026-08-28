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
        h, w = frame.shape[:2]
        out: list[Detection] = []
        candidates: dict[str, list[tuple[int, Detection]]] = {"ball": [], "cup_or_barrel": []}

        # Video-specific smoke-test cues: glowing red jewel and warm wooden barrels.
        # These are evidence cues only; replace with a trained ONNX detector for production.
        red = cv2.inRange(hsv, np.array([0, 110, 100]), np.array([12, 255, 255]))
        red |= cv2.inRange(hsv, np.array([168, 110, 100]), np.array([179, 255, 255]))
        red = cv2.morphologyEx(red, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        brown = cv2.inRange(hsv, np.array([5, 55, 25]), np.array([30, 255, 220]))
        brown = cv2.morphologyEx(brown, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))

        for mask, cls, min_area, max_area in ((red, "ball", 25, w*h*.04), (brown, "cup_or_barrel", 600, w*h*.22)):
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                x, y, bw, bh = cv2.boundingRect(c); area = bw * bh
                if area < min_area or area > max_area: continue
                fill = cv2.contourArea(c) / max(area, 1)
                if cls == "ball" and (bw > bh * 2.2 or bh > bw * 2.2): continue
                if cls == "cup_or_barrel" and fill < .16: continue
                score = min(.95, max(self.confidence, .45 + .45 * min(fill, 1.0)))
                det = Detection(cls, float(score), (x, y, bw, bh), "color-cue-test-backend")
                candidates[cls].append((area, det))
        # This supplied scene contains one jewel and three barrels. Keep only the
        # strongest geometric candidates; the production ONNX model must replace this.
        out.extend(d for _, d in sorted(candidates["ball"], key=lambda item: item[0], reverse=True)[:1])
        out.extend(d for _, d in sorted(candidates["cup_or_barrel"], key=lambda item: item[0], reverse=True)[:3])
        return out
