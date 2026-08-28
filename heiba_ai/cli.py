from __future__ import annotations

import argparse
import json
from pathlib import Path
from .application.analysis import AnalysisCancelled, AnalysisEngine
from .inference.providers import InferenceProviderSelector

EXIT = {"ok":0, "input":2, "decode":3, "model":4, "inference":5, "no_decision":6, "cancelled":7}

def build_parser():
    p=argparse.ArgumentParser(prog="heiba-cli", description="Local Heiba AI Analysis CLI")
    sub=p.add_subparsers(dest="command", required=True)
    a=sub.add_parser("analyze"); a.add_argument("--input", required=True); a.add_argument("--output", required=True); a.add_argument("--detector", default="yolo11-onnx"); a.add_argument("--tracker", default="bytetrack"); a.add_argument("--profile", default="balanced"); a.add_argument("--provider", default="auto"); a.add_argument("--export-video", action="store_true"); a.add_argument("--export-json", action="store_true"); a.add_argument("--export-csv", action="store_true")
    b=sub.add_parser("benchmark"); b.add_argument("--dataset", required=True); b.add_argument("--model", required=True)
    sub.add_parser("diagnose"); return p

def main(argv=None):
    args=build_parser().parse_args(argv)
    if args.command == "diagnose": print(json.dumps(InferenceProviderSelector("auto").as_dict(), indent=2)); return 0
    if args.command == "benchmark":
        print(json.dumps({"status":"not_run","dataset":args.dataset,"model":args.model,"message":"Provide a labeled dataset; no accuracy is claimed without benchmark evidence."}, indent=2)); return 0
    src=Path(args.input)
    if not src.exists() or not src.is_file(): print("Invalid input / مدخل غير صالح"); return EXIT["input"]
    try:
        result=AnalysisEngine().analyze(src, Path(args.output), args.provider, args.profile, args.tracker, args.export_video, lambda f,*_: print(f"progress={f:.3f}"))
        print(json.dumps(result["decision"], ensure_ascii=False, indent=2)); return EXIT["no_decision"] if result["decision"]["state"] == "NO_DECISION" else 0
    except AnalysisCancelled: return EXIT["cancelled"]
    except ValueError as e: print(str(e)); return EXIT["decode"]
    except Exception as e: print(f"Inference failure / فشل الاستدلال: {e}"); return EXIT["inference"]

if __name__ == "__main__": raise SystemExit(main())
