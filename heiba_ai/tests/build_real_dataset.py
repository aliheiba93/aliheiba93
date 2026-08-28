from __future__ import annotations
from pathlib import Path
import cv2, numpy as np, random, shutil

VIDEO=Path('/home/ubuntu/upload/ScreenRecording_08-25-202609-48-24_1(2).mov')
ROOT=Path('/home/ubuntu/aliheiba93/training/barrels_jewel')
random.seed(7)
for split in ('train','val','test'):
    (ROOT/'images'/split).mkdir(parents=True,exist_ok=True); (ROOT/'labels'/split).mkdir(parents=True,exist_ok=True)
cap=cv2.VideoCapture(str(VIDEO)); total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); frame=0
# Leave temporal gaps: validation/test are separate contiguous windows.
while True:
    ok, img=cap.read()
    if not ok: break
    if frame % 2:
        frame += 1; continue
    if frame < int(total*.65): split='train'
    elif frame < int(total*.82): split='val'
    else: split='test'
    name=f'{frame:06d}'; cv2.imwrite(str(ROOT/'images'/split/f'{name}.jpg'),img)
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); h,w=img.shape[:2]; labels=[]
    red=cv2.inRange(hsv,np.array([0,85,80]),np.array([28,255,255])); red |= cv2.inRange(hsv,np.array([165,85,80]),np.array([179,255,255]))
    red=cv2.morphologyEx(red,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    contours,_=cv2.findContours(red,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    balls=[]
    for c in contours:
        x,y,bw,bh=cv2.boundingRect(c); area=bw*bh; fill=cv2.contourArea(c)/max(area,1)
        if 20<=area<=w*h*.04 and .25<=fill<=1 and .45<=bw/max(bh,1)<=2.2: balls.append((area,x,y,bw,bh))
    if balls:
        _,x,y,bw,bh=max(balls)
        labels.append(f'0 {(x+bw/2)/w:.6f} {(y+bh/2)/h:.6f} {bw/w:.6f} {bh/h:.6f}')
    brown=cv2.inRange(hsv,np.array([3,40,20]),np.array([32,255,235])); brown=cv2.morphologyEx(brown,cv2.MORPH_CLOSE,np.ones((13,13),np.uint8))
    contours,_=cv2.findContours(brown,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE); barrels=[]
    for c in contours:
        x,y,bw,bh=cv2.boundingRect(c); area=bw*bh; fill=cv2.contourArea(c)/max(area,1)
        if 900<=area<=w*h*.22 and fill>=.18 and .35<=bw/max(bh,1)<=1.6: barrels.append((area,x,y,bw,bh))
    for _,x,y,bw,bh in sorted(barrels,reverse=True)[:3]: labels.append(f'1 {(x+bw/2)/w:.6f} {(y+bh/2)/h:.6f} {bw/w:.6f} {bh/h:.6f}')
    (ROOT/'labels'/split/f'{name}.txt').write_text('\n'.join(labels)+'\n',encoding='utf-8')
    frame += 1
cap.release()
(ROOT/'data.yaml').write_text('path: '+str(ROOT).replace('\\','/')+'\ntrain: images/train\nval: images/val\ntest: images/test\nnc: 2\nnames: [ball, cup_or_barrel]\n',encoding='utf-8')
print('dataset',ROOT)
for split in ('train','val','test'):
    print(split,len(list((ROOT/'images'/split).glob('*.jpg'))),len(list((ROOT/'labels'/split).glob('*.txt'))))
