#!/usr/bin/env python3
"""Preserve one completed or failed run without replaying any calculation."""
import argparse
import datetime
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            value.update(block)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--archive-dir", required=True)
    args = parser.parse_args()
    root = Path(args.run_dir).resolve(strict=True)
    destination = Path(args.archive_dir).resolve()
    if destination.is_relative_to(root) or root.is_relative_to(destination):
        raise ValueError("run and archive directories must be separate")
    destination.mkdir(parents=True, exist_ok=True)
    files = []
    for directory, names, leaves in os.walk(root, followlinks=False):
        base = Path(directory)
        names[:] = sorted(name for name in names
                          if name not in (".git", "target", "vigilode", "rust_bridge")
                          and not (base/name).is_symlink())
        for name in sorted(leaves):
            path = base/name
            if path.is_symlink() or not path.is_file():
                raise ValueError("non-regular run evidence: " + str(path))
            files.append((str(path.relative_to(root)), path))
    # Include raw compiled library when a reused or new build is identified.
    summary = root/"SUMMARY.json"
    build = None
    if summary.is_file():
        build = Path(json.loads(summary.read_text())["bridge_build"])
    elif (root/"build/BUILD_IDENTITY.json").is_file():
        build = root/"build"
    elif (root/"BRIDGE_INTAKE.json").is_file():
        accepted = [item for item in json.loads((root/"BRIDGE_INTAKE.json").read_text()).get("inspected", [])
                    if item.get("status") == "VALID_REUSED"]
        if accepted:
            build = Path(accepted[0]["receipt"]).parent
    if build is not None:
        for relative in ("BUILD_IDENTITY.json", "target/release/libhe29_optimized_bridge.so"):
            path = build/relative
            if path.is_symlink() or not path.is_file():
                raise ValueError("missing raw bridge evidence: " + str(path))
            files.append(("bridge_artifact/"+Path(relative).name, path))
    manifest = {name: {"bytes": path.stat().st_size, "sha256": sha(path)} for name,path in files}
    if len(manifest) != len(files) or not files:
        raise ValueError("empty or duplicate evidence set")
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    pending = destination / ("HE29_HPC64_RETURN_"+stamp+".tar.gz.partial")
    with pending.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name,path in files:
                    # Hash before and after read; do not package live-changing evidence.
                    archive.add(path, arcname=name, recursive=False)
                    if path.stat().st_size != manifest[name]["bytes"] or sha(path) != manifest[name]["sha256"]:
                        raise RuntimeError("evidence changed during packaging: " + name)
                content=(json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode()
                info=tarfile.TarInfo("MANIFEST.json"); info.size=len(content)
                archive.addfile(info,io.BytesIO(content))
        raw.flush();os.fsync(raw.fileno())
    with tarfile.open(pending,"r:gz") as archive:
        members=archive.getmembers()
        if len(members)!=len(files)+1 or any(not member.isfile() for member in members):
            raise ValueError("archive membership")
        for name,expected in manifest.items():
            stream=archive.extractfile(name); value=hashlib.sha256(); size=0
            for block in iter(lambda: stream.read(1024*1024),b""):
                value.update(block);size+=len(block)
            if value.hexdigest()!=expected["sha256"] or size!=expected["bytes"]:
                raise ValueError("archive payload readback: "+name)
    checksum=sha(pending)
    final=destination/("HE29_HPC64_RETURN_"+stamp+"_"+checksum[:8]+".tar.gz")
    os.link(pending,final);pending.unlink()
    receipt={"archive":str(final),"bytes":final.stat().st_size,"sha256":checksum,
        "payloads_verified":len(files),"regular_members":len(files)+1,
        "status":"LOCAL_RAW_PAYLOAD_READBACK_PASS","provider_upload":"NOT_PERFORMED",
        "scientific_admission":"READ_RESULT_OR_FAILURE_SEPARATELY"}
    with (destination/(final.name+".json")).open("x") as stream:
        json.dump(receipt,stream,indent=2);stream.write("\n");stream.flush();os.fsync(stream.fileno())
    descriptor=os.open(destination,os.O_RDONLY)
    try: os.fsync(descriptor)
    finally: os.close(descriptor)
    print(json.dumps(receipt,indent=2))


if __name__=="__main__":
    main()
