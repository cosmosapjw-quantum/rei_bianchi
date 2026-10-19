#!/usr/bin/env python3
"""Read-only selected source identities and add-only VigilODE reuse origin copy."""
import datetime
import hashlib
import json
import pathlib
import stat
import subprocess
import sys

REPO = pathlib.Path("/tmp/rei_vigilode_research")
OUT = pathlib.Path("/tmp/rei_run18_work/inventory")
HEAD = "ac1cd2a4738c2441c92e5fdae5f70aba35e53544"
PATHS = [
    "README.md", "LICENSE", "Cargo.toml", "Cargo.lock", "rust-toolchain.toml",
    "crates/rodas5p-core/Cargo.toml",
    "crates/rodas5p-integrators/Cargo.toml",
    "crates/rodas5p-core/src/error.rs",
    "crates/rodas5p-core/src/directed.rs",
    "crates/rodas5p-core/src/operator.rs",
    "crates/rodas5p-core/src/nonnormal_certificate.rs",
    "crates/rodas5p-core/src/residual_gain.rs",
    "crates/rodas5p-integrators/src/problem.rs",
    "crates/rodas5p-integrators/src/dense_output_v2.rs",
    "crates/rodas5p-integrators/src/bound_pr101.rs",
    "crates/rodas5p-integrators/src/bound_collective.rs",
    "crates/rodas5p-integrators/src/gray_scott.rs",
    "crates/rodas5p-integrators/src/certification.rs",
    "crates/rodas5p-integrators/src/outward_certificate.rs",
    "crates/rodas5p-core/tests/safe_enclosure_exp_floor.rs",
    "crates/rodas5p-core/tests/safe_enclosure_probes.rs",
    "crates/rodas5p-integrators/tests/a05_dense_global_output.rs",
    "crates/rodas5p-integrators/tests/production_audit_pr101_provider.rs",
    "crates/rodas5p-integrators/tests/production_audit_bound_collective.rs",
    "crates/rodas5p-integrators/tests/a11_gray_scott_log_norm.rs",
    "docs/reviews/20261018_production_audit/REPORT_KO.md",
    "docs/reviews/20261011_promotion_theory/CERTIFICATE_ATLAS_KO.md",
    "research/production_audit_20261018/DECISION.json",
    "research/production_audit_20261018_followup/FINDINGS_STATUS.json",
    "research/production_audit_20261018_a07_gate_correction/DECISION.json",
    "research/component_triage_20261019/COMPONENTS.json",
    "research/component_triage_20261019/PREREGISTRATION.md",
    "research/benchmark_results_20261019/README.md",
    "research/benchmark_results_20261019/run1/REPORT_KO.md",
    "research/benchmark_results_20261019/run2/REPORT_KO.md",
    "research/strict_solver_comparison_20261019/PREREGISTRATION.md",
    "research/strict_solver_comparison_20261019/runs/39252371864/status.json",
    "research/strict_solver_comparison_20261019/runs/39253322042/status.json",
]
COPY = ["LICENSE", "crates/rodas5p-core/src/directed.rs", "crates/rodas5p-core/src/error.rs",
        "Cargo.toml", "crates/rodas5p-core/Cargo.toml", "rust-toolchain.toml"]
commands = []
def git(*args):
    cmd = ["git", "-C", str(REPO), *args]
    p = subprocess.run(cmd, capture_output=True, check=False)
    commands.append({"argv": cmd, "exit_code": p.returncode, "stdout": p.stdout.decode(), "stderr": p.stderr.decode()})
    if p.returncode:
        raise RuntimeError("read-only Git command failed")
    return p.stdout

def identity(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}

def write_new(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw: raise RuntimeError(f"refuse differing existing file: {path}")
    else:
        with path.open("xb") as f: f.write(raw)

actual_head = git("rev-parse", "HEAD").decode().strip()
if actual_head != HEAD: raise RuntimeError("checkout HEAD mismatch")
tree_id = git("rev-parse", "HEAD^{tree}").decode().strip()
raw_tree = git("ls-tree", "-r", "-z", "--full-tree", "HEAD")
tree = {}
for entry in raw_tree.split(b"\0"):
    if not entry: continue
    meta, name = entry.split(b"\t", 1)
    mode, kind, sha = meta.decode().split()
    tree[name.decode()] = {"git_mode": mode, "type": kind, "git_blob": sha}
records = []
copies = []
for name in PATHS:
    path = REPO / name
    if not stat.S_ISREG(path.lstat().st_mode): raise RuntimeError(f"not ordinary source: {name}")
    raw = path.read_bytes()
    ident = identity(raw)
    target = tree[name]
    if target["git_mode"] not in ("100644", "100755") or target["git_blob"] != ident["git_blob"]:
        raise RuntimeError(f"source Git blob mismatch: {name}")
    rec = {"path": name, **ident, "git_mode": target["git_mode"],
           "url": f"https://github.com/cosmosapjw-quantum/vigilode/blob/{HEAD}/{name}"}
    records.append(rec)
    if name in COPY:
        dst = OUT / "reuse_origin" / name
        write_new(dst, raw)
        if dst.read_bytes() != raw: raise RuntimeError("copied origin mismatch")
        copies.append({"path": str(dst.relative_to(OUT)), "original_path": name, **ident})
git("diff", "--exit-code")
git("diff", "--cached", "--exit-code")
after_head = git("rev-parse", "HEAD").decode().strip()
if after_head != HEAD: raise RuntimeError("HEAD changed during inventory")
record = {
    "schema": "rei.run18.vigilode-selected-source-readback.v1",
    "time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "checkout": str(REPO), "head": HEAD, "tree": tree_id,
    "status": "ESTABLISHED_SELECTED_SOURCE_BYTE_IDENTITY",
    "selected_files": records, "selected_file_count": len(records),
    "selected_file_bytes": sum(r["bytes"] for r in records),
    "source_copies": copies,
    "AGENTS_files_in_complete_git_tree": [name for name in tree if pathlib.PurePosixPath(name).name == "AGENTS.md"],
    "unchanged_tracked_source": True, "source_or_remote_mutations": 0,
    "native_builds": 0, "tests_executed": 0, "native_rhs_calls": 0, "quadratures": 0, "IVPs": 0,
    "claim_scope": "Byte identity and source contracts only. Producer tests are archived evidence, not re-executed here.",
    "invocation": [sys.executable, "-B", str(pathlib.Path(__file__).resolve())],
    "git_commands": commands,
}
# Full ls-tree data is already parsed into selected identities; avoid duplicating 6k-path text.
for cmd in record["git_commands"]:
    if "ls-tree" in cmd["argv"]:
        raw = cmd.pop("stdout").encode()
        cmd["stdout_summary"] = {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "git_tree": tree_id}
write_new(OUT / "SOURCE_READBACK_CHECK.json", (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode())
print(json.dumps({"status": record["status"], "selected_files": len(records),
                  "bytes": record["selected_file_bytes"], "exact_origin_copies": len(copies),
                  "new_IVPs": 0, "tests_executed": 0}))

