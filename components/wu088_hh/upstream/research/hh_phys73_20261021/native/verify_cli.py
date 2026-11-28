#!/usr/bin/env python3
"""Small protocol/guard checks using manufactured data, with create-only receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import time


def payload(d: list[complex], t: list[complex], x: list[complex], tasks: int = 1) -> bytes:
    assert len(d) == len(t) == len(x)
    block = b"".join(struct.pack("<dd", z.real, z.imag) for array in (d, t, x) for z in array)
    return b"HHG73V01" + struct.pack("<QQ", tasks, len(d)) + block * tasks


def verify(binary: Path) -> dict:
    commands = []
    with tempfile.TemporaryDirectory(prefix="phys73_cli_") as directory:
        root = Path(directory)
        good = payload([0j, 1 + 0j, 2 + 0j], [0j, 1 + 0j, 1 + 0j], [1 + 0j, 2 + 0j, 3 + 0j])

        def run(name: str, data: bytes, flags: list[str], expected: int = 0, env=None, stale=False):
            source, output = root / (name + ".bin"), root / (name + ".out")
            source.write_bytes(data)
            if stale:
                output.write_bytes(b"preserve-existing-output")
            argv = [str(binary), str(source), str(output), *flags]
            start = time.perf_counter()
            completed = subprocess.run(argv, capture_output=True, text=True, env=env)
            elapsed = time.perf_counter() - start
            assert completed.returncode == expected, (name, completed.stderr)
            assert source.read_bytes() == data, name
            if expected:
                assert not completed.stdout, name
                if stale:
                    assert output.read_bytes() == b"preserve-existing-output", name
                else:
                    assert not output.exists(), name
                metadata = None
            else:
                metadata = json.loads(completed.stdout)
                expected_size = 24 + 16 * metadata["tasks"] * metadata["nodes"]
                raw = output.read_bytes()
                assert len(raw) == expected_size and raw[:8] == b"HHO73V01", name
                assert struct.unpack_from("<QQ", raw, 8) == (metadata["tasks"], metadata["nodes"]), name
                assert metadata["certified"] is False and metadata["HH_R10"] == "OFF", name
                assert len(metadata["kernel_seconds"]) == metadata["repeat"], name
            commands.append({"name": name, "argv": argv, "exit_code": completed.returncode,
                             "wall_seconds": elapsed, "stdout": completed.stdout, "stderr": completed.stderr,
                             "input_sha256": hashlib.sha256(data).hexdigest(), "passed": True})
            return metadata, output.read_bytes() if output.exists() else None

        a, raw = run("single", good, ["--workers", "64", "--repeat", "3"])
        assert struct.unpack_from("<6d", raw, 24) == (0.0, 0.0, 5.0, 0.0, 8.0, 0.0)
        assert a["workers_effective"] == 1
        _, dense = run("dense", good, ["--mode", "dense"])
        assert raw == dense
        seven = payload([0j, 1 + 0j, 2 + 0j], [0j, 1 + 0j, 1 + 0j], [1 + 0j, 2 + 0j, 3 + 0j], 7)
        a, multi = run("multi", seven, ["--workers", "6"])
        assert a["workers_effective"] == min(6, a["available_parallelism"])
        _, serial = run("serial", seven, ["--workers", "1"])
        assert multi == serial
        a, _ = run("underflow", payload([complex(1e-300, 0)], [0j], [complex(1e-100, 0)]), [])
        assert a["multiplication_underflow_to_zero_all_repeats"] > 0
        run("overflow", payload([complex(1e308, 0)], [0j], [complex(1e308, 0)]), [], 2)
        run("bad_magic", b"BADMAGIC" + good[8:], [], 2)
        run("truncated", good[:-1], [], 2)
        run("trailing", good + b"x", [], 2)
        run("nan", payload([complex(float("nan"), 0)], [0j], [1 + 0j]), [], 2)
        run("sentinel", payload([1 + 0j], [1 + 0j], [1 + 0j]), [], 2)
        run("workers_zero", good, ["--workers", "0"], 2)
        run("duplicate", good, ["--repeat", "1", "--repeat", "1"], 2)
        run("stale", good, [], 2, stale=True)
        bad_env = dict(os.environ, HH_R10="ON")
        run("hh_r10", good, [], 2, env=bad_env)
        run("dense_limit", payload([0j] * 32_000, [0j] * 32_000, [0j] * 32_000), ["--mode", "dense"], 2)

    return {"schema": "PHYS73_NATIVE_CLI_CHECK_V1", "scope": "manufactured protocol checks; no HH campaign",
            "binary_sha256": hashlib.file_digest(binary.open("rb"), "sha256").hexdigest(),
            "successful_processes": sum(x["exit_code"] == 0 for x in commands),
            "expected_rejections": sum(x["exit_code"] != 0 for x in commands),
            "checks_passed": len(commands), "commands": commands}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.receipt.exists():
        parser.error("receipt exists; use a new path")
    record = verify(args.binary.resolve())
    with args.receipt.open("x") as output:
        json.dump(record, output, indent=2)
        output.write("\n")
    print(json.dumps({k: v for k, v in record.items() if k != "commands"}, indent=2))


if __name__ == "__main__":
    main()
