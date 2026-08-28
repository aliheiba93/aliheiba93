# ONNX Training Report

## Source and labels

The model was trained from the supplied `ScreenRecording_08-25-202609-48-24_1(2).mov`. The source contains 366 H.264 frames at approximately 59.82 FPS and 1288x634 resolution. Frames were sampled every second frame and split by time into 119 training images, 31 validation images, and 33 holdout test images. The classes are `ball` (the orange/red faceted jewel in this video) and `cup_or_barrel` (wooden barrels).

Labels were generated from conservative color and geometry cues and are therefore **weak/pseudo-labels**, not human-reviewed ground truth. This is useful for fitting the supplied rendered scene but is not sufficient for claiming scientific accuracy.

## Training

The model starts from YOLO11n pretrained weights and was fine-tuned on CPU for 29 epochs with early stopping. The exported model is `heiba_barrels_jewel.onnx`, input `[1,3,640,640]`, ONNX opset 12, SHA-256 `f0156a6412ee6dc9938bc64cc3a0e55cb4100c279475be259f272b824d0f8987`.

## Holdout results

| Metric | Holdout value |
|---|---:|
| Box precision | 0.519 |
| Box recall | 0.839 |
| mAP@0.50 | 0.565 |
| mAP@0.50:0.95 | 0.552 |

These values are measured on a temporally held-out portion of the same short video using weak labels. They do not establish generalization to other recordings, resolutions, lighting, camera angles, or game assets.

## Application result

The integrated ONNX model was run over all 366 frames of the supplied video. Both classes were observed, 65 real jewel-to-barrel temporal links were recorded, and the application returned `LOW_CONFIDENCE` rather than `NO_DECISION`. This is intentional: the evidence is present, but confidence calibration and human-reviewed labels are not yet sufficient for a final high-confidence decision.

To move beyond `LOW_CONFIDENCE`, provide several independently recorded videos and human-reviewed frame/track annotations, then retrain and calibrate on disjoint validation and test sets.
