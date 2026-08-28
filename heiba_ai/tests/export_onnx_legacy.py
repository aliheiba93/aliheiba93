from pathlib import Path
import hashlib, json, torch
from ultralytics import YOLO

root=Path('/home/ubuntu/aliheiba93'); best=root/'training/runs/barrels_jewel/weights/best.pt'; out=root/'training/barrels_jewel/heiba_barrels_jewel.onnx'
y=YOLO(str(best)); net=y.model.float().eval(); dummy=torch.zeros(1,3,640,640)
with torch.no_grad():
    torch.onnx.export(net,dummy,str(out),opset_version=12,input_names=['images'],output_names=['output'],dynamic_axes=None,do_constant_folding=True,dynamo=False)
manifest={"name":"heiba-barrels-jewel-yolo11n","version":"0.1.0-video-fit","sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"classes":["ball","cup_or_barrel"],"class_notes":{"ball":"orange/red faceted jewel in supplied video"},"input_size":[640,640],"opset":12,"verification_status":"trained-on-single-video; holdout metrics required","training_source":"ScreenRecording_08-25-202609-48-24_1(2).mov","warning":"Video-specific model; not general accuracy evidence."}
(root/'training/barrels_jewel/model_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); print(out); print(json.dumps(manifest,ensure_ascii=False))
