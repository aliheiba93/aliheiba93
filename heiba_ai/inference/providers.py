from __future__ import annotations

import importlib.util
import platform
from dataclasses import dataclass, asdict


@dataclass
class ProviderInfo:
    name: str
    version: str
    reason: str
    available: bool


class InferenceProviderSelector:
    def __init__(self, requested: str = "auto"):
        self.requested = requested

    def select(self) -> ProviderInfo:
        ort_available = importlib.util.find_spec("onnxruntime") is not None
        if self.requested == "cpu" or (self.requested == "auto" and ort_available):
            version = "unavailable" if not ort_available else self._ort_version()
            return ProviderInfo("ORT CPU", version, "Safe universal fallback; no GPU assumption", ort_available)
        if self.requested in {"cuda", "tensorrt", "openvino", "windowsml"}:
            return ProviderInfo(self.requested.upper(), "not loaded", "Requested provider is not bundled or verified on this host", False)
        return ProviderInfo("OpenCV CPU", platform.python_version(), "Heuristic test backend; ONNX Runtime is optional", True)

    @staticmethod
    def _ort_version() -> str:
        try:
            import onnxruntime as ort
            return ort.__version__
        except Exception:
            return "unknown"

    def as_dict(self):
        return asdict(self.select())
