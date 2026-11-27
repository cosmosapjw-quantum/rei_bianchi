#!/usr/bin/env python3
"""Build the strict Fortran kernel and record exact compiler/source identities."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("strict", "debug"), default="strict")
    parser.add_argument("--native", action="store_true", help="optional local-CPU ISA; not portable")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    output = (args.output_dir or here / ("build-debug" if args.mode == "debug" else "build")).resolve()
    compiler = shutil.which(os.environ.get("FC", "gfortran"))
    if not compiler:
        raise SystemExit("gfortran compiler unavailable; install the documented build dependency")
    version = subprocess.check_output([compiler, "--version"], text=True)
    if "GNU Fortran" not in version:
        raise SystemExit("this audited build profile currently supports GNU Fortran only")
    # Flags are closed here: externally supplied FFLAGS do not bypass the
    # floating-point contract. No OpenMP reduction, BLAS, or -ffast-math.
    flags = ["-O3" if args.mode == "strict" else "-O0", "-std=f2008", "-fPIC",
             "-shared", "-fopenmp", "-fno-fast-math", "-ffp-contract=off",
             "-fno-associative-math", "-Wall", "-Wextra"]
    if args.mode == "debug":
        flags += ["-g", "-fcheck=all", "-fbacktrace", "-ffpe-trap=invalid,zero,overflow"]
    if args.native:
        flags.append("-march=native")
    source = here / "inner_product.f90"
    frontend_name = subprocess.check_output([compiler, "-print-prog-name=f951"], text=True).strip()
    frontend = Path(frontend_name).resolve()
    output.mkdir(parents=True, exist_ok=True)
    library = output / "libbass_inner.so"
    with tempfile.TemporaryDirectory(prefix="bass-native-", dir=output) as temporary:
        work = Path(temporary)
        staged = work / library.name
        vectorization = work / "vectorization.txt"
        command = [compiler, *flags, "-fopt-info-vec-optimized=" + str(vectorization),
                   "-J", str(work), str(source), "-o", str(staged)]
        completed = subprocess.run(command, cwd=work, capture_output=True, text=True)
        if completed.returncode:
            raise SystemExit(completed.stdout + completed.stderr)
        sha = hashlib.sha256(staged.read_bytes()).hexdigest()
        metadata = {
            "schema": "bass-inner-build-v1", "built_utc": datetime.now(timezone.utc).isoformat(),
            "mode": args.mode, "native_cpu_isa": args.native,
            "compiler_path": compiler, "compiler_version": version,
            "compiler_target": subprocess.check_output([compiler, "-dumpmachine"], text=True).strip(),
            "compiler_sha256": hashlib.sha256(Path(compiler).read_bytes()).hexdigest(),
            "compiler_sha256_scope": "invoked compiler path; may be a toolchain wrapper",
            "fortran_frontend_path": str(frontend),
            "fortran_frontend_sha256": hashlib.sha256(frontend.read_bytes()).hexdigest() if frontend.is_file() else None,
            "flags": flags, "command": command, "source": source.name,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "library_sha256": sha, "library_bytes": staged.stat().st_size,
            "machine": platform.machine(), "platform": platform.platform(),
            "build_stdout": completed.stdout, "build_stderr": completed.stderr,
            "vectorization_report": vectorization.read_text() if vectorization.exists() else "",
            "arithmetic_contract": "binary64; fixed point/patch order; no reassociation/FMA contraction; SIMD independent entries",
            "abi": 1,
        }
        staged.replace(library)
        library.with_suffix(".build.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"library": str(library), "sha256": sha, "mode": args.mode,
                      "native_cpu_isa": args.native}))


if __name__ == "__main__":
    main()
