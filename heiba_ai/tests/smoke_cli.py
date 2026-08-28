from pathlib import Path
import tempfile
import cv2
import numpy as np
from heiba_ai.application.analysis import AnalysisEngine
from heiba_ai.storage.repository import LocalRepository

root=Path(tempfile.mkdtemp(prefix="heiba-smoke-")); video=root/"sample.mp4"; out=root/"export"
w=cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*"mp4v"), 8, (320,240))
for i in range(8):
    frame=np.zeros((240,320,3),dtype=np.uint8); cv2.rectangle(frame,(50+i*3,80,100,160),(80,150,210),-1); cv2.circle(frame,(75+i*3,115),12,(220,220,220),-1); w.write(frame)
w.release()
r=AnalysisEngine(LocalRepository(root/"data")).analyze(video,out,export_video=True)
required={"annotated.mp4","analysis.json","tracks.csv","events.csv","diagnostics.json","manifest.json"}
assert required <= {p.name for p in out.iterdir()}
print(root)
