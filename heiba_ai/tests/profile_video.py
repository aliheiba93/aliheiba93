from pathlib import Path
import cv2
from heiba_ai.vision.detector import Detector
p=Path('/home/ubuntu/upload/ScreenRecording_08-25-202609-48-24_1(2).mov')
cap=cv2.VideoCapture(str(p)); d=Detector(); counts=[]
while True:
    ok,frame=cap.read()
    if not ok: break
    ds=d.detect(frame); counts.append((len([x for x in ds if x.cls=='cup_or_barrel']),len([x for x in ds if x.cls=='ball'])))
cap.release()
print('frames',len(counts),'cup_minmax',min(x[0] for x in counts),max(x[0] for x in counts),'ball_minmax',min(x[1] for x in counts),max(x[1] for x in counts))
print('sample',counts[::max(1,len(counts)//12)])
