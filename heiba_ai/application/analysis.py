from __future__ import annotations

import csv
import json
import time
import math
from dataclasses import asdict
from pathlib import Path
from typing import Callable
import cv2

from heiba_ai.inference.providers import InferenceProviderSelector
from heiba_ai.storage.repository import LocalRepository, sha256_file
from heiba_ai.vision.detector import Detector
from heiba_ai.vision.tracker import ByteTrack

EVENTS = ["INITIALIZED", "BALL_VISIBLE", "BALL_COVERED", "SHUFFLE_STARTED", "OCCLUDED", "REVEAL", "FINAL_STABLE", "INTERRUPTED"]

class AnalysisCancelled(Exception): pass

class AnalysisEngine:
    def __init__(self, repo: LocalRepository | None = None):
        self.repo = repo or LocalRepository()

    def validate_video(self, path: Path) -> dict:
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened(): raise ValueError("Unable to decode video / تعذر فتح ملف الفيديو")
        meta = {"fps": float(cap.get(cv2.CAP_PROP_FPS) or 0), "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), "codec": "OpenCV/FFmpeg"}
        cap.release()
        if meta["fps"] <= 0 or meta["width"] <= 0 or meta["height"] <= 0: raise ValueError("Invalid video metadata / بيانات الفيديو غير صالحة")
        return meta

    def analyze(self, input_path: Path, output_dir: Path | None = None, provider="auto", profile="balanced", tracker_name="bytetrack", export_video=True, progress: Callable | None = None, cancelled: Callable[[], bool] | None = None) -> dict:
        meta = self.validate_video(input_path)
        job_id, default_dir = self.repo.create_job(input_path)
        out = Path(output_dir) if output_dir else default_dir; out.mkdir(parents=True, exist_ok=True)
        selected = InferenceProviderSelector(provider).select()
        candidates = [
            Path(__file__).resolve().parents[2] / "training" / "barrels_jewel" / "heiba_barrels_jewel.onnx",
            Path(__file__).resolve().parents[2] / "packaging" / "models" / "heiba_barrels_jewel.onnx",
            Path(getattr(__import__('sys'), '_MEIPASS', Path.cwd())) / "models" / "heiba_barrels_jewel.onnx",
            Path.cwd() / "models" / "heiba_barrels_jewel.onnx",
        ]
        bundled_model = next((p for p in candidates if p.exists()), None)
        detector = Detector(bundled_model, confidence=.3 if profile == "fast" else .4)
        tracker = ByteTrack()
        cap = cv2.VideoCapture(str(input_path)); writer = None
        if export_video:
            writer = cv2.VideoWriter(str(out / "annotated.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), meta["fps"], (meta["width"], meta["height"]))
        rows, events, frame_samples = [], [], []; start = time.perf_counter(); balls_seen = 0; cup_ids = set(); dropped = 0; ball_links = []; last_ball_link = None
        events.append({"name":"INITIALIZED", "frame":0, "timestamp":0.0, "evidence":"analysis_started"})
        total = max(meta["frame_count"], 1); frame_index = 0
        while True:
            if cancelled and cancelled(): raise AnalysisCancelled()
            ok, frame = cap.read()
            if not ok: break
            detections = detector.detect(frame); tracks = tracker.update(detections)
            balls = [t for t in tracks if t.cls == "ball" and not t.predicted]
            cups = [t for t in tracks if t.cls == "cup_or_barrel" and not t.predicted]
            balls_seen += bool(balls); cup_ids.update(t.track_id for t in cups)
            if balls and cups:
                ball = balls[0]; bx, by = ball.bbox[0] + ball.bbox[2] / 2, ball.bbox[1] + ball.bbox[3] / 2
                nearest = min(cups, key=lambda t: math.hypot((t.bbox[0]+t.bbox[2]/2)-bx, (t.bbox[1]+t.bbox[3]/2)-by))
                cx, cy = nearest.bbox[0] + nearest.bbox[2]/2, nearest.bbox[1] + nearest.bbox[3]/2
                distance = math.hypot(cx-bx, cy-by)
                if distance <= max(140.0, nearest.bbox[2] * 1.25):
                    last_ball_link = {"track_id": nearest.track_id, "distance_px": round(distance,2), "ball_track_id": ball.track_id, "frame": frame_index}
                    ball_links.append(last_ball_link)
            timestamp = frame_index / meta["fps"]
            if balls and (not events or events[-1]["name"] != "BALL_VISIBLE"): events.append({"name":"BALL_VISIBLE","frame":frame_index,"timestamp":timestamp,"evidence":"real_detection"})
            if frame_index == max(1, total // 3): events.append({"name":"SHUFFLE_STARTED","frame":frame_index,"timestamp":timestamp,"evidence":"timeline_marker"})
            for t in tracks:
                row = {"frame":frame_index,"timestamp":timestamp,"track_id":t.track_id,"class":t.cls,"x":t.bbox[0],"y":t.bbox[1],"w":t.bbox[2],"h":t.bbox[3],"score":t.score,"age":t.age,"missed":t.missed_frames,"vx":t.velocity_px[0],"vy":t.velocity_px[1],"association_cost":t.association_cost,"predicted":t.predicted}
                rows.append(row)
                if len(frame_samples) < 240 and frame_index % max(1, total // 120) == 0: frame_samples.append(row)
                if writer and not t.predicted:
                    x,y,w,h=t.bbox; color=(40,210,100) if t.cls=="cup_or_barrel" else (40,180,240); cv2.rectangle(frame,(x,y),(x+w,y+h),color,2); cv2.putText(frame,f"{t.cls} #{t.track_id} {t.score:.2f}",(x,max(18,y-5)),cv2.FONT_HERSHEY_SIMPLEX,.5,color,1,cv2.LINE_AA)
            if writer: writer.write(frame)
            frame_index += 1
            if progress: progress(min(1.0, frame_index / total), frame_index, frame_samples[-1:] if frame_samples else [])
        cap.release()
        if writer: writer.release()
        decision = "NO_DECISION"; reason = "No validated post-shuffle ball-to-cup evidence; human review required."
        if last_ball_link and len(ball_links) >= 3:
            decision = "LOW_CONFIDENCE"
            reason = "A real jewel-to-barrel temporal association was observed, but post-shuffle evidence or calibration is insufficient; human review required."
        confidence = {"ball_visibility_ratio": balls_seen / max(frame_index,1), "tracked_cups": len(cup_ids), "evidence_frames": balls_seen, "temporal_links": len(ball_links), "last_ball_link": last_ball_link, "calibration": "not_calibrated"}
        result = {"job_id":job_id,"input":str(input_path),"metadata":meta,"provider":asdict(selected),"profile":profile,"tracker":tracker.name,"model":{"name":detector.model_name,"verified":False},"frame_samples":frame_samples,"events":events,"ball_links":ball_links[:500],"decision":{"state":decision,"reason":reason,"confidence_components":confidence},"paths":{}}
        (out / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        with (out / "tracks.csv").open("w", newline="", encoding="utf-8") as f:
            if rows: w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        with (out / "events.csv").open("w", newline="", encoding="utf-8") as f:
            w=csv.DictWriter(f, fieldnames=["name","frame","timestamp","evidence"]); w.writeheader(); w.writerows(events)
        diagnostics={"provider":asdict(selected),"fps_input":meta["fps"],"frames_processed":frame_index,"dropped_frames":dropped,"latency_ms_avg":round((time.perf_counter()-start)*1000/max(frame_index,1),3),"tracker":tracker.name}
        (out / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
        manifest={"job_id":job_id,"input_sha256":sha256_file(input_path),"outputs":{p.name:sha256_file(p) for p in out.iterdir() if p.is_file() and p.name != "manifest.json"}}
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        result["paths"]={p.name:str(p) for p in out.iterdir()}; return result
