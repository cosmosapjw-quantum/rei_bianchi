"""Install only the three inspected attached Rust components; no science build."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, time

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / "selected_distribution"
PREFIX = ROOT / "prefix"
RECEIPT = ROOT / "INSTALL_PROBE_RECEIPT.json"
if RECEIPT.exists() or PREFIX.exists():
    raise SystemExit("create-only prefix/receipt already exists")
components = ["rustc", "cargo", "rust-std-x86_64-unknown-linux-gnu"]
for component in components:
    for line in (STAGE / component / "manifest.in").read_text().splitlines():
        kind, rel = line.split(":", 1)
        if kind != "file" or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise SystemExit("unsafe component manifest")
        if not (STAGE / component / rel).is_file():
            raise SystemExit("missing component input")
commands = []
env = os.environ.copy()
env["PATH"] = str(PREFIX / "bin") + ":" + env.get("PATH", "")
env["LD_LIBRARY_PATH"] = str(PREFIX / "lib")
def run(argv, tag, timeout=30):
    start = time.perf_counter()
    p = subprocess.run(argv, cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
    (ROOT / (tag + ".stdout.txt")).write_text(p.stdout)
    (ROOT / (tag + ".stderr.txt")).write_text(p.stderr)
    row = {"argv": argv, "exit_code": p.returncode, "wall_seconds": time.perf_counter()-start,
           "stdout": tag+".stdout.txt", "stderr": tag+".stderr.txt"}
    commands.append(row)
    return p
install = run(["sh", str(STAGE / "install.sh"), "--prefix="+str(PREFIX),
               "--components="+",".join(components), "--disable-ldconfig"], "install")
if install.returncode == 0:
    run([str(PREFIX / "bin/rustc"), "--version", "--verbose"], "rustc_version")
    run([str(PREFIX / "bin/cargo"), "--version"], "cargo_version")
    source = ROOT / "compiler_probe.rs"
    source.write_text('fn main() { let x = std::hint::black_box(1.25_f64); println!("{:.17e}", x.exp()); }\n')
    c = run([str(PREFIX / "bin/rustc"), "--edition=2024", str(source), "-o", str(ROOT / "compiler_probe")], "compile_probe")
    if c.returncode == 0:
        run([str(ROOT / "compiler_probe")], "run_probe")
files = [{"path": str(p.relative_to(PREFIX)), "bytes": p.stat().st_size,
          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
         for p in sorted(PREFIX.rglob("*")) if p.is_file()] if PREFIX.exists() else []
receipt = {"schema": "REI_RUN19_RUNTIME_INSTALL_V1", "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "prefix": str(PREFIX), "components": components, "commands": commands,
           "environment_overrides": {"PATH_prefix": str(PREFIX / "bin"), "LD_LIBRARY_PATH": str(PREFIX / "lib")},
           "prefix_files": files, "prefix_bytes": sum(r["bytes"] for r in files),
           "archive_signature_verified": False, "scientific_native_builds": 0, "rhs_calls": 0, "ivps": 0}
RECEIPT.write_text(json.dumps(receipt, indent=2)+"\n")
print(json.dumps({"commands": commands, "prefix_bytes": receipt["prefix_bytes"]}, indent=2))
