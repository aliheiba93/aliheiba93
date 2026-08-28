# Heiba AI Analysis

**Heiba AI Analysis** is a local Windows desktop workstation for forensic video analysis and research and development only. It is not a gambling or financial-decision application. The current implementation provides a PySide6 GUI, a local CLI, auditable tracking evidence, conservative temporal decision output, local SQLite settings/jobs, feedback capture, export manifests, and a truthful CPU fallback.

> The included detector backend is explicitly a smoke-test backend. No production accuracy claim is made. Replace it with a domain-trained ONNX detector and a labeled benchmark before any scientific or operational claim.

## Run from source

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements-lock.txt
python -m heiba_ai.main
python -m heiba_ai.cli diagnose
```

## CLI

```text
heiba-cli.exe analyze --input "C:\Videos\recording.mov" --output "C:\Exports\job-001" --detector yolo11-onnx --tracker bytetrack --profile balanced --provider auto --export-video --export-json --export-csv
heiba-cli.exe benchmark --dataset "D:\HeibaDataset\test" --model models\cup_bal
heiba-cli.exe diagnose
```

Exit codes are 0 success, 2 invalid input, 3 decode failure, 4 missing/incompatible model, 5 inference failure, 6 valid `NO_DECISION`, and 7 cancellation.

## Test and Windows build

```powershell
python -m pytest
pip install pyinstaller
pyinstaller packaging/heiba.spec
# Compile packaging/HeibaAI.iss with Inno Setup on Windows.
```

The build is intentionally folder-based rather than one-file so models, FFmpeg, and DLLs remain maintainable. The Windows CI workflow tests and builds the project on `windows-latest`.

## Layout

`heiba_ai/ui` contains GUI components; `application` contains temporal analysis; `vision` contains detector/tracker interfaces; `inference` contains provider selection; `media` is reserved for media adapters; `storage` contains SQLite and local dataset handling; `heiba_ai/tests` contains tests; `packaging` contains model manifest, PyInstaller, and Inno Setup definitions; `docs` contains bilingual user and developer guidance.
