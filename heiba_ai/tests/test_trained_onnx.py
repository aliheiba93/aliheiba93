from pathlib import Path
import cv2
from heiba_ai.vision.detector import Detector

VIDEO=Path('/home/ubuntu/upload/ScreenRecording_08-25-202609-48-24_1(2).mov')
MODEL=Path('/home/ubuntu/aliheiba93/training/barrels_jewel/heiba_barrels_jewel.onnx')

def main():
    assert MODEL.exists()
    d=Detector(MODEL, confidence=.25); assert d.session is not None
    cap=cv2.VideoCapture(str(VIDEO)); seen=set(); n=0
    while True:
        ok,frame=cap.read()
        if not ok: break
        seen.update(x.cls for x in d.detect(frame)); n+=1
    cap.release(); print('frames',n,'classes',sorted(seen))

if __name__=='__main__': main()
