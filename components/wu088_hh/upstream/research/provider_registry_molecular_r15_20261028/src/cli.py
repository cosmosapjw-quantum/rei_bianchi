"""Create-only JSON CLI for the R15 exact conditional comparison."""
import argparse
import json
from pathlib import Path
import sys


def main():
    sys.set_int_max_str_digits(6000)
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("R15 CLI output must not already exist")
    from cubic_convolution import run_case, serializable
    try:
        case = json.loads(args.input.read_text(encoding="utf-8"))
        result = {"status": "COMPUTED_CONDITIONAL", "result": serializable(run_case(case))}
        code = 0
    except Exception as exc:
        result = {"status": "FAIL", "exception_type": type(exc).__name__, "message": str(exc)}
        code = 1
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
