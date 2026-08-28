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
    def as_dict(self): return asdict(self)

class Detector:
    """ONNX detector with an explicit color-cue smoke-test fallback."""
    classes = ("ball", "cup_or_barrel")
    def __init__(self, model_path: Path | None = None, confidence: float = .35):
        self.model_path, self.confidence = model_path, confidence
        self.model_name = "unverified-test-backend" if model_path is None else model_path.name
        self.session = None
        if model_path and model_path.exists():
            try:
                import onnxruntime as ort
                self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
                self.input_name = self.session.get_inputs()[0].name
            except Exception:
                self.session = None

    def detect(self, frame: np.ndarray) -> list[Detection]:
        if frame is None or frame.size == 0: return []
        if self.session is not None:
            try: return self._detect_onnx(frame)
            except Exception: pass
        return self._detect_color_cue(frame)

    def _detect_onnx(self, frame):
        h, w = frame.shape[:2]; size=640; scale=min(size/w,size/h); nw,nh=int(w*scale),int(h*scale)
        resized=cv2.resize(frame,(nw,nh)); canvas=np.full((size,size,3),114,np.uint8); px=(size-nw)//2; py=(size-nh)//2; canvas[py:py+nh,px:px+nw]=resized
        inp=canvas[:,:,::-1].transpose(2,0,1).astype(np.float32)/255.0; raw=self.session.run(None,{self.input_name:inp[None]})[0]
        pred=np.asarray(raw); pred=pred[0].T if pred.ndim==3 and pred.shape[1] < pred.shape[2] else pred[0]
        boxes=[]; scores=[]; labels=[]
        for row in pred:
            if len(row)<6: continue
            cx,cy,bw,bh=row[:4]; cls_scores=row[4:]; ci=int(np.argmax(cls_scores)); score=float(cls_scores[ci])
            if score < self.confidence: continue
            x=int((cx-bw/2-px)/scale); y=int((cy-bh/2-py)/scale); ww=int(bw/scale); hh=int(bh/scale)
            x=max(0,min(w-1,x)); y=max(0,min(h-1,y)); ww=max(1,min(w-x,ww)); hh=max(1,min(h-y,hh)); boxes.append([x,y,ww,hh]); scores.append(score); labels.append(ci)
        out=[]
        for ci in set(labels):
            inds=[i for i,c in enumerate(labels) if c==ci]
            keep=cv2.dnn.NMSBoxes([boxes[i] for i in inds],[scores[i] for i in inds],self.confidence,.45)
            for k in np.array(keep).reshape(-1) if len(keep) else []:
                i=inds[int(k)]; out.append(Detection(self.classes[ci] if ci<len(self.classes) else str(ci),scores[i],tuple(boxes[i]),"onnx"))
        return out

    def _detect_color_cue(self, frame):
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV); h,w=frame.shape[:2]; candidates={"ball":[],"cup_or_barrel":[]}
        red=cv2.inRange(hsv,np.array([0,85,80]),np.array([28,255,255])); red |= cv2.inRange(hsv,np.array([165,85,80]),np.array([179,255,255])); red=cv2.morphologyEx(red,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
        brown=cv2.inRange(hsv,np.array([3,40,20]),np.array([32,255,235])); brown=cv2.morphologyEx(brown,cv2.MORPH_CLOSE,np.ones((13,13),np.uint8))
        for mask,cls,min_area,max_area in ((red,"ball",20,w*h*.04),(brown,"cup_or_barrel",600,w*h*.22)):
            contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                x,y,bw,bh=cv2.boundingRect(c); area=bw*bh; fill=cv2.contourArea(c)/max(area,1)
                if area<min_area or area>max_area or (cls=="ball" and (bw>bh*2.2 or bh>bw*2.2)) or (cls=="cup_or_barrel" and fill<.16): continue
                score=min(.95,max(self.confidence,.45+.45*min(fill,1.0))); candidates[cls].append((area,Detection(cls,float(score),(x,y,bw,bh),"color-cue-test-backend")))
        return [d for _,d in sorted(candidates["ball"],reverse=True)[:1]]+[d for _,d in sorted(candidates["cup_or_barrel"],reverse=True)[:3]]
