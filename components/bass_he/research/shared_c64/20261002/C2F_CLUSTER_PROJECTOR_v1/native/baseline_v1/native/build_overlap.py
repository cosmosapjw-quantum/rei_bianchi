#!/usr/bin/env python3
"""Build strict/debug weighted overlap with create-only durable evidence."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import uuid

BASE_FLAGS = ["-std=f2008", "-fPIC", "-shared", "-fopenmp", "-cpp",
              "-fno-fast-math", "-fno-associative-math", "-ffp-contract=off",
              "-fprotect-parens", "-Wall", "-Wextra"]
DEBUG_FLAGS = ["-g", "-fcheck=all", "-fbacktrace", "-ffpe-trap=invalid,zero,overflow"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_create(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)  # create-only: preserve previous evidence
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("strict", "debug"), default="strict")
    parser.add_argument("--compiler", default="gfortran")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    output = (args.output_dir or here / ("build" if args.mode == "strict" else "build-debug")).resolve()
    output.mkdir(parents=True, exist_ok=True)
    record = {"schema": "bass-he.c2f.native-build.v1", "mode": args.mode,
              "started_utc": datetime.now(timezone.utc).isoformat()}
    try:
        prohibited = {key: os.environ[key] for key in ("FFLAGS", "FCFLAGS", "LDFLAGS") if os.environ.get(key)}
        if prohibited:
            raise ValueError("external FFLAGS/FCFLAGS/LDFLAGS are not accepted by this closed build profile")
        compiler = shutil.which(args.compiler)
        if not compiler:
            raise RuntimeError("GNU Fortran unavailable; supply --compiler with its explicit path")
        version = subprocess.check_output([compiler, "--version"], text=True)
        if "GNU Fortran" not in version:
            raise RuntimeError("this versioned build profile supports GNU Fortran only")
        source = here / "weighted_overlap.f90"
        digest = sha(source)
        flags = ["-O3" if args.mode == "strict" else "-O0", *BASE_FLAGS]
        if args.mode == "debug":
            flags += DEBUG_FLAGS
        flags += ['-DBASS_OVERLAP_SOURCE_SHA="' + digest + '"']
        library = output / "libbass_overlap.so"
        metadata_path = library.with_suffix(".build.json")
        report_path = output / "vectorization.txt"
        if any(path.exists() for path in (library, metadata_path, report_path)):
            raise FileExistsError("output exists: select a new --output-dir; evidence is create-only")
        with tempfile.TemporaryDirectory(prefix=".compile-", dir=output) as temporary:
            work = Path(temporary)
            staged = work / library.name
            vectorization = work / "vectorization.txt"
            command = [compiler, *flags, "-fopt-info-vec-all=" + str(vectorization),
                       "-J", str(work), str(source), "-o", str(staged)]
            completed = subprocess.run(command, cwd=work, capture_output=True, text=True)
            record.update(command=command, compiler_path=compiler, compiler_version=version,
                          compiler_target=subprocess.check_output([compiler, "-dumpmachine"], text=True).strip(),
                          compiler_sha256=sha(compiler),
                          compiler_sha256_scope="invoked path; may be wrapper", flags=flags,
                          build_stdout=completed.stdout, build_stderr=completed.stderr,
                          returncode=completed.returncode, source=source.name, source_sha256=digest)
            if completed.returncode:
                raise RuntimeError("Fortran compiler failed; see preserved build-failure record")
            frontend = Path(subprocess.check_output([compiler, "-print-prog-name=f951"], text=True).strip()).resolve()
            vector_bytes = vectorization.read_bytes() if vectorization.exists() else b""
            record.update(status="BUILD_SUCCEEDED", abi=1, binary64=True, complex128=True,
                          tile_rows=256, portable_isa=True, dynamic_threading_allowed=False,
                          fortran_frontend_path=str(frontend),
                          fortran_frontend_sha256=sha(frontend) if frontend.is_file() else None,
                          library_sha256=sha(staged), library_bytes=staged.stat().st_size,
                          vectorization_report=report_path.name,
                          vectorization_sha256=hashlib.sha256(vector_bytes).hexdigest(),
                          machine=platform.machine(), platform=platform.platform(),
                          completed_utc=datetime.now(timezone.utc).isoformat(),
                          numerical_contract="binary64 products; SIMD independent products; fixed row-order Neumaier sums; OpenMP independent output elements; no reassociation or FMA contraction",
                          runtime_contract="explicit positive OMP_NUM_THREADS and OMP_DYNAMIC=FALSE; caller bounds total ranks times threads")
            atomic_create(library, staged.read_bytes())
            atomic_create(report_path, vector_bytes)
            atomic_create(metadata_path, (json.dumps(record, indent=2) + "\n").encode())
        print(json.dumps({"library": str(library), "mode": args.mode,
                          "library_sha256": record["library_sha256"], "source_sha256": digest}))
    except BaseException as exc:
        record.update(status="BUILD_FAILED", error_type=type(exc).__name__, error=str(exc),
                      failed_utc=datetime.now(timezone.utc).isoformat())
        failure = output / ("BUILD_FAILURE_" + uuid.uuid4().hex + ".json")
        atomic_create(failure, (json.dumps(record, indent=2) + "\n").encode())
        raise


if __name__ == "__main__":
    main()
