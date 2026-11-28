"""Run one NEW reference check, preserving first stdout/stderr and run identity."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024**2, 256 * 1024**2))
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024**2, 8 * 1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))


run_id, script = sys.argv[1:3]
if not run_id.replace("_", "").isalnum():
    raise ValueError("simple immutable run id required")
script = (ROOT / script).resolve()
if ROOT not in script.parents:
    raise ValueError("script must be in this package")
dest = ROOT / "evidence" / run_id
dest.mkdir(parents=True, exist_ok=False)
started = datetime.now(timezone.utc).isoformat()
start = time.monotonic()
timeout = False
with (dest / "stdout.txt").open("wb") as out, (dest / "stderr.txt").open("wb") as err:
    try:
        process = subprocess.run([sys.executable, str(script)], cwd=ROOT,
                                 stdout=out, stderr=err, timeout=30, preexec_fn=limits,
                                 env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        code = process.returncode
    except subprocess.TimeoutExpired:
        code, timeout = 124, True
elapsed = time.monotonic() - start
payload = {"schema": "WU088_HH_PHYS06_BOUNDED_EXECUTION_V1", "run_id": run_id,
    "script": str(script.relative_to(ROOT)), "started_utc": started,
    "elapsed_seconds": elapsed, "exit_code": code, "timeout": timeout,
    "wall_limit_seconds": 30, "address_space_limit_MiB": 256,
    "log_file_limit_MiB_each": 8, "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
    "files": {p.name: {"bytes": p.stat().st_size,
                        "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
              for p in dest.iterdir()},
    "native_endpoint_runs": 0, "native_root_runs": 0, "IVP_runs": 0,
    "historical_suite_replays": 0}
(dest / "EXECUTION.json").write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps(payload, indent=2))
sys.exit(code)
