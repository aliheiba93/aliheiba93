from __future__ import annotations

from dataclasses import dataclass, asdict
import math
from .detector import Detection

@dataclass
class Track:
    track_id: int
    cls: str
    bbox: tuple[int, int, int, int]
    score: float
    age: int = 1
    missed_frames: int = 0
    velocity_px: tuple[float, float] = (0.0, 0.0)
    association_cost: float = 0.0
    appearance_similarity: float | None = None
    predicted: bool = False

    def as_dict(self): return asdict(self)

class ByteTrack:
    name = "ByteTrack"
    def __init__(self, max_missed: int = 15, match_distance: float = 120.0):
        self.max_missed, self.match_distance = max_missed, match_distance
        self.tracks: list[Track] = []
        self.next_id = 1

    @staticmethod
    def _center(box): return (box[0] + box[2] / 2, box[1] + box[3] / 2)

    def update(self, detections: list[Detection]) -> list[Track]:
        used = set()
        for t in self.tracks:
            best, best_i = None, None
            tc = self._center(t.bbox)
            for i, d in enumerate(detections):
                if i in used or d.cls != t.cls: continue
                dc = self._center(d.bbox)
                dist = math.hypot(tc[0] - dc[0], tc[1] - dc[1])
                if dist <= self.match_distance and (best is None or dist < best): best, best_i = dist, i
            if best_i is not None:
                d = detections[best_i]; old = self._center(t.bbox); new = self._center(d.bbox)
                t.velocity_px = (new[0]-old[0], new[1]-old[1]); t.bbox = d.bbox; t.score = d.score
                t.association_cost = float(best); t.appearance_similarity = None; t.missed_frames = 0; t.age += 1; t.predicted = False; used.add(best_i)
            else:
                t.bbox = (int(t.bbox[0]+t.velocity_px[0]), int(t.bbox[1]+t.velocity_px[1]), t.bbox[2], t.bbox[3])
                t.missed_frames += 1; t.age += 1; t.predicted = True
        for i, d in enumerate(detections):
            if i not in used:
                self.tracks.append(Track(self.next_id, d.cls, d.bbox, d.score)); self.next_id += 1
        self.tracks = [t for t in self.tracks if t.missed_frames <= self.max_missed]
        return [t for t in self.tracks]
