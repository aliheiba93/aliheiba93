from pathlib import Path
import cv2
import numpy as np
from heiba_ai.vision.detector import Detection
from heiba_ai.vision.tracker import ByteTrack
from heiba_ai.application.analysis import AnalysisEngine
from heiba_ai.storage.repository import LocalRepository

def test_tracker_keeps_real_id():
    tr=ByteTrack(); a=tr.update([Detection("cup_or_barrel", .8, (10,10,30,40))]); b=tr.update([Detection("cup_or_barrel", .8, (14,11,30,40))]); assert a[0].track_id == b[0].track_id; assert b[0].association_cost > 0

def test_mov_h264_like_fixture_opens(tmp_path):
    p=tmp_path/"fixture.mp4"; writer=cv2.VideoWriter(str(p),cv2.VideoWriter_fourcc(*"mp4v"),10,(160,120));
    for _ in range(3): writer.write(np.zeros((120,160,3),np.uint8))
    writer.release(); assert AnalysisEngine(LocalRepository(tmp_path/"data")).validate_video(p)["frame_count"] == 3

def test_overlay_data_has_tracker_fields():
    t=ByteTrack().update([Detection("ball",.7,(2,3,4,5))])[0].as_dict(); assert {"track_id","bbox","score","age","missed_frames","velocity_px","association_cost"} <= set(t)

def test_heuristic_never_claims_full_reid():
    assert "HSV" not in ByteTrack.name and ByteTrack.name == "ByteTrack"
