from pathlib import Path
import hashlib, json
from ultralytics import YOLO

ROOT=Path('/home/ubuntu/aliheiba93/training/barrels_jewel')
RUNS=Path('/home/ubuntu/aliheiba93/training/runs')
model=YOLO('yolo11n.pt')
model.train(data=str(ROOT/'data.yaml'), epochs=35, imgsz=640, batch=4, workers=2, device='cpu', patience=10, project=str(RUNS), name='barrels_jewel', exist_ok=True, pretrained=True, seed=7, verbose=False)
best=RUNS/'barrels_jewel'/'weights'/'best.pt'
trained=YOLO(str(best)); trained.export(format='onnx', imgsz=640, opset=17, simplify=False, dynamic=False)
onnx=best.with_suffix('.onnx')
h=hashlib.sha256(onnx.read_bytes()).hexdigest()
manifest={"name":"heiba-barrels-jewel-yolo11n","version":"0.1.0-video-fit","sha256":h,"classes":["ball","cup_or_barrel"],"class_notes":{"ball":"orange/red faceted jewel in supplied video"},"input_size":[640,640],"opset":17,"verification_status":"trained-on-single-video; holdout metrics required","training_source":"ScreenRecording_08-25-202609-48-24_1(2).mov","warning":"This model is video-specific and must not be treated as general accuracy evidence."}
out=ROOT/'model_manifest.json'; out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); print(onnx); print(out)
