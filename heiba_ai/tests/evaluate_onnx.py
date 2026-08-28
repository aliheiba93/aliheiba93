from pathlib import Path
import json
from ultralytics import YOLO
root=Path('/home/ubuntu/aliheiba93'); model=root/'training/runs/barrels_jewel/weights/best.pt'; data=root/'training/barrels_jewel/data.yaml'
r=YOLO(str(model)).val(data=str(data), split='test', imgsz=640, device='cpu', project=str(root/'training/runs'), name='test_eval', exist_ok=True, verbose=False)
metrics={'box_precision':float(r.box.mp),'box_recall':float(r.box.mr),'map50':float(r.box.map50),'map50_95':float(r.box.map)}
(root/'training/barrels_jewel/test_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8'); print(json.dumps(metrics))
