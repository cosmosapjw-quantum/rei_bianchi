#!/usr/bin/env python3
"""RUN18 fixed-commit delivery verification; no scientific module imports or execution."""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import subprocess
import sys
import time

PARENT = "0e23addf4fefa69287d4626622bf97505677ea43"
PREFIX = "research/atomic_nuclear_ssot_20261017/run18/"
MANIFEST_SHA = "4362a1cc976e5075d7946aa4a1518413917d121d54705fe8cfc80e64465d1221"
EXPECTED_FILES = 130
EXPECTED_BYTES = 7241027

def ident(raw: bytes) -> dict:
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "git_blob": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()}

def safe(value: str) -> str:
    if (not isinstance(value, str) or not value or "\\" in value
        or PurePosixPath(value).is_absolute()
        or any(p in ("", ".", "..") for p in value.split("/"))):
        raise ValueError("unsafe relative path")
    return value

def ordinary(path: Path) -> bytes:
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("nonordinary canonical file: " + str(path))
    return path.read_bytes()

def write_new(path: Path, raw: bytes) -> None:
    with path.open("xb") as f:
        f.write(raw)

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--canonical", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--tree", required=True)
    a = ap.parse_args()
    for sha in (a.commit, a.tree):
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("full lowercase Git SHA required")
    repo, canonical, out = a.repo.resolve(), a.canonical.resolve(), a.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "rei.run18.science-git-readback.v1",
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "repository": "cosmosapjw-quantum/rei_bianchi",
        "commit": a.commit, "tree": a.tree, "required_immediate_parent": PARENT,
        "checkout": str(repo), "canonical": str(canonical),
        "commands": [], "invocation": [sys.executable, "-B", *sys.argv],
        "environment": {"python": sys.version, "executable": sys.executable,
                        "platform": platform.platform(), "GIT_OPTIONAL_LOCKS": "0"},
        "execution_counts": {"tests": 0, "builds": 0, "native_RHS": 0,
                             "quadratures": 0, "IVPs": 0, "certificate_replays": 0},
        "scope": "Parent/tree identity,130add-onlypaths,Git blobs/modes and exact canonical/manifest bytes only."
    }
    env = dict(os.environ)
    env["GIT_OPTIONAL_LOCKS"] = "0"

    def git(label: str, parts: list[str], data: bytes | None = None, save_stdout: bool = True) -> bytes:
        argv = ["git", "-C", str(repo), *parts]
        start = time.monotonic()
        p = subprocess.run(argv, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        row = {"argv": argv, "exit_code": p.returncode, "wall_seconds": time.monotonic()-start,
               "stdout_identity": ident(p.stdout), "stderr_identity": ident(p.stderr)}
        if save_stdout:
            name = label + ".stdout"; write_new(out/name, p.stdout); row["stdout"] = name
        else:
            row["stdout_storage"] = "Hash only; exact Git blob bytes compared with canonical and manifest in memory."
        name = label + ".stderr"; write_new(out/name, p.stderr); row["stderr"] = name
        if data is not None:
            name = label + ".stdin"; write_new(out/name, data); row["stdin"] = name
        report["commands"].append(row)
        if p.returncode:
            raise RuntimeError("Git command failed: " + label)
        return p.stdout

    try:
        before = git("head_before", ["rev-parse", "HEAD", "HEAD^{tree}"]).decode().splitlines()
        ip = Path(git("index_path", ["rev-parse", "--git-path", "index"]).decode().strip())
        if not ip.is_absolute():
            ip = repo/ip
        index_before = ident(ordinary(ip))
        fixed = git("fixed_objects", ["rev-parse", a.commit, a.commit+"^{tree}"]).decode().splitlines()
        if fixed != [a.commit, a.tree]:
            raise ValueError("fixed source/tree mismatch")
        commit_raw = git("commit_object", ["cat-file", "-p", a.commit])
        header = commit_raw.split(b"\n\n", 1)[0].decode().splitlines()
        parents = [line.split(" ",1)[1] for line in header if line.startswith("parent ")]
        trees = [line.split(" ",1)[1] for line in header if line.startswith("tree ")]
        if parents != [PARENT] or trees != [a.tree]:
            raise ValueError("exact immediate parent/tree mismatch")
        report["commit_object"] = {"identity": ident(commit_raw), "parents": parents, "tree": trees[0]}

        rawtree = git("run18_tree", ["ls-tree", "-r", "-z", "--full-tree", a.commit, "--", PREFIX.rstrip("/")])
        entries = {}
        for row in rawtree.split(b"\0"):
            if not row:
                continue
            meta, name = row.split(b"\t",1)
            mode, kind, blob = meta.decode().split()
            path = name.decode()
            if not path.startswith(PREFIX):
                raise ValueError("unexpected tree prefix")
            rel = safe(path[len(PREFIX):])
            if rel in entries or kind != "blob" or mode not in ("100644","100755"):
                raise ValueError("nonordinary or duplicate tree entry")
            entries[rel] = {"git_mode": mode, "git_blob": blob}
        if len(entries) != EXPECTED_FILES:
            raise ValueError("expected exactly130run18paths")

        rawdiff = git("parent_to_science_delta", ["diff-tree","--no-commit-id","--raw","-r","-z",PARENT,a.commit])
        chunks = rawdiff.split(b"\0");pos = 0;delta = []
        while pos < len(chunks) and chunks[pos]:
            oldmode, mode, old, new, status = chunks[pos].decode().lstrip(":").split()
            path = chunks[pos+1].decode();pos += 2
            if status != "A" or oldmode != "000000" or old != "0"*40 or not path.startswith(PREFIX):
                raise ValueError("global delta includes modification/deletion/out-of-scope path")
            rel = safe(path[len(PREFIX):])
            if entries.get(rel) != {"git_mode":mode,"git_blob":new}:
                raise ValueError("delta and new tree mismatch")
            delta.append(rel)
        if len(delta) != EXPECTED_FILES or set(delta) != set(entries):
            raise ValueError("global delta is not exactly130science additions")
        report["delta"] = {"additions":len(delta),"modifications":0,"deletions":0,
                           "out_of_run18_changes":0,"all_new_tree_paths_match":True,
                           "raw_identity":ident(rawdiff)}

        blob_ids = list(dict.fromkeys(row["git_blob"] for row in entries.values()))
        data = ("\n".join(blob_ids)+"\n").encode()
        batch = git("science_blobs", ["cat-file","--batch"], data, False)
        offset = 0;blobs = {}
        for expected in blob_ids:
            end = batch.index(b"\n", offset)
            h = batch[offset:end].decode().split()
            if len(h) != 3 or h[0] != expected or h[1] != "blob":
                raise ValueError("Git blob header mismatch")
            size = int(h[2]);raw = batch[end+1:end+1+size];offset = end+1+size
            if batch[offset:offset+1] != b"\n" or ident(raw)["git_blob"] != expected:
                raise ValueError("Git blob bytes/framing mismatch")
            offset += 1;blobs[expected] = raw
        if offset != len(batch):
            raise ValueError("unexpected extra blob data")

        raw_manifest = blobs[entries["SCIENCE_MANIFEST.json"]["git_blob"]]
        if ident(raw_manifest)["sha256"] != MANIFEST_SHA:
            raise ValueError("remote manifest SHA mismatch")
        if raw_manifest != ordinary(canonical/"SCIENCE_MANIFEST.json"):
            raise ValueError("canonical manifest bytes differ")
        manifest = json.loads(raw_manifest)
        if (manifest.get("schema") != "rei.run18.complete-science-manifest.v1"
            or not manifest.get("excludes_itself") or manifest["parent_commit"] != PARENT
            or manifest["file_count_excluding_this_manifest"] != 129
            or manifest["payload_bytes_excluding_this_manifest"] != 7206416):
            raise ValueError("manifest contract mismatch")
        rows = manifest["files"]
        if len(rows)!=129 or len({r["path"] for r in rows})!=129:
            raise ValueError("manifest cardinality mismatch")
        if {safe(r["path"]) for r in rows}|{"SCIENCE_MANIFEST.json"} != set(entries):
            raise ValueError("manifest/tree path membership mismatch")

        checks = []
        fullrows = [*rows, {"path":"SCIENCE_MANIFEST.json",**ident(raw_manifest),"git_mode":"100644"}]
        for row in fullrows:
            rel = row["path"];raw = blobs[entries[rel]["git_blob"]];actual = ident(raw)
            if any(actual[k] != row[k] for k in ("bytes","sha256","git_blob")):
                raise ValueError("manifest identity mismatch: " + rel)
            if entries[rel]["git_mode"] != row["git_mode"]:
                raise ValueError("manifest Git mode mismatch: " + rel)
            p = canonical/rel
            if ordinary(p) != raw:
                raise ValueError("canonical bytes mismatch: " + rel)
            mode = stat.S_IMODE(p.stat().st_mode)
            if mode != (0o755 if row["git_mode"]=="100755" else 0o644):
                raise ValueError("canonical filesystem mode mismatch: " + rel)
            checks.append({"path":rel,**actual,"git_mode":row["git_mode"],"canonical_mode":format(mode,"04o"),
                           "manifest_match":True,"canonical_byte_match":True})
        if sum(x["bytes"] for x in checks) != EXPECTED_BYTES:
            raise ValueError("total science bytes mismatch")
        report["science"] = {"files":checks,"file_count":130,"bytes":EXPECTED_BYTES,
                             "manifest":ident(raw_manifest),"all_paths_hashes_blobs_modes_match":True}

        git("tracked_diff_after", ["diff","--exit-code"])
        git("cached_diff_after", ["diff","--cached","--exit-code"])
        after = git("head_after", ["rev-parse","HEAD","HEAD^{tree}"]).decode().splitlines()
        index_after = ident(ordinary(ip))
        if before != after or index_before != index_after:
            raise ValueError("existing HEAD/index changed")
        report["preserved_checkout"] = {"HEAD_tree_before_after":before,"index_before":index_before,
                                         "index_after":index_after,"tracked_diff_empty":True,
                                         "cached_diff_empty":True,"canonical_source_writes":0}
        report["status"] = "VERIFIED_RUN18_SCIENCE130_GIT_READBACK"
        report["scope_limits"] = [
            "No numerical recomputation, old trajectory rerun, validation test replay, native call or build.",
            "Original RUN17/RUN13 byte-restoration work was not repeated.",
            "Fetched commit/tree and all130science blobs are available in the existing isolated Git object store."]
        exit_code = 0
    except Exception as exc:
        report["status"] = "BLOCKED_RUN18_SCIENCE_READBACK"
        report["error"] = {"type":type(exc).__name__,"message":str(exc)}
        exit_code = 1
    report["ended_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    raw = (json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode()
    write_new(out/"RUN18_SCIENCE_READBACK.json",raw)
    print(json.dumps({"status":report["status"],"receipt":str(out/"RUN18_SCIENCE_READBACK.json"),**ident(raw)}))
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())

