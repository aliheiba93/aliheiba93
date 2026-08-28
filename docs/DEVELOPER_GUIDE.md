# Developer Guide

## Local setup

Use Python 3.11 on Windows. Create a virtual environment, install `requirements-lock.txt`, and run `python -m heiba_ai.main` for the GUI or `python -m heiba_ai.cli diagnose` for diagnostics. The default fallback detector is explicitly test-only and must not be used to claim production accuracy.

## Build

Run `pyinstaller packaging/heiba.spec`, copy the generated `dist/HeibaAI` and `dist/heiba-cli` folders into the release workspace, then compile `packaging/HeibaAI.iss` with Inno Setup. Zip the same two folders plus the model manifest as `HeibaAI-Portable-x64.zip`. A production release must add a verified domain-trained ONNX model, update its SHA-256 manifest, run the labeled benchmark, and sign the installer with Authenticode when a certificate is available.

## Evidence rules

Every overlay is derived from decoded frame data. A predicted track is never promoted to final evidence. The decision layer defaults to `NO_DECISION`; accuracy and calibrated probabilities require a separate labeled validation/test process. Do not add hard-coded boxes, fake confidence values, or fabricated benchmark reviews.
