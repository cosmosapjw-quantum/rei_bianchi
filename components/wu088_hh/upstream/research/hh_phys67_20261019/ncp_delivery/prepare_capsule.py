#!/usr/bin/env python3
"""Package the existing PHYS66 runner; never execute a numerical case."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from wu088_hh.phys66_campaign import CODE, SOURCE, case_specs
from wu088_hh.phys63_lap_contract import source_guard

VERSIONS = {"numpy": "2.3.5", "scipy": "1.17.0", "mpmath": "1.3.0"}
SOURCE_INPUTS = CODE + ["src/wu088_hh/__init__.py", SOURCE,
    "research/hh_phys65_20261018/r5/PROOF.md",
    "research/hh_phys66_20261018/r5/PROOF.md"]

README = """# PHYS66 longtail: NCP 실행용 완성 runner

## 현재 상태

이 capsule은 기존 PHYS66 C5–C8 runner의 exact source 파일을 담는다.
PHYS64의 완료된 20건과 기존 smoke/pilot은 실행 대상에 없다.
현재 상태는 **PREPARED / NOT_SUBMITTED**다. 이 capsule을 만드는 과정에서
새 longtail case를 실행하지 않았다. NCP에서 할 일은 환경 준비·preflight와
완성된 명령 실행이며, solver 설계를 NCP에 넘기지 않는다.

원본 frozen NPZ SHA256:
`f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d`.
`MANIFEST.json`과 `SHA256SUMS`는 모든 payload의 정확한 bytes를 고정한다.
base git HEAD는 당시 저장소의 HEAD만 뜻하며, manifest로 고정된 복원
runner overlay가 이미 그 commit에 게시되었다고 뜻하지 않는다.

## 의존성과 host 준비

Python 3.12 환경을 권장한다. 준비 단계에서 실제 확인한 Python은
3.12.14이며 numpy2.3.5/scipy1.17.0/mpmath1.3.0을 사용했다.
`requirements-pinned.txt`에는 정확한 package version이 있다. 이 source
capsule에는 Python interpreter나 platform wheel을 넣지 않았다.
NCP host의 실제 import와 hardware는 아래 preflight에서 확인한다.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-pinned.txt
.venv/bin/python verify_capsule.py
```

기존에 세 package가 설치된 적절한 Python이 있으면 그 interpreter를
`NCP_PYTHON`으로 지정해도 된다. 실행 결과에는 실제 package versions와
Python build 문자열이 포함된다. 환경 차이는 새로운 fingerprint가 된다.

## preflight와 단일 프로세스 실행

capsule 디렉터리에서 다음을 실행한다. 두 번째 명령이 실제 과학 실행이다.
prepared capsule 검증에서는 첫 번째 명령만 수행했다.

```bash
NCP_PYTHON=.venv/bin/python bash run_preflight.sh
NCP_PYTHON=.venv/bin/python bash run_longtail.sh
```

실제 runner 명령은 다음과 같다.

```bash
.venv/bin/python scripts/phys66_ncp.py --profile longtail \\
  --out runs/phys66_longtail --workers 1 --memory-gib 4 --timeout 900 --resume
```

`workers=1`, BLAS/OpenMP thread=1, worker address-space limit=4GiB,
각 case wall limit=900초다. 6개의 worker wall limit 합은 최대5400초이며,
preflight·결과 묶음 생성 시간은 별도다. 실제 실행 시간·peak RSS는 결과에서
확인한다. 이 설정으로 동시 실행하는 numerical worker는 한 개다.

## 고정된 6개 요청

`REQUESTS_LONGTAIL.json`은 실제 `case_specs('longtail')`로 생성했다.

| L | ell 목록 | T/a0 |
|---:|---|---:|
| 28 | 0..28 | 55 |
| 28 | 0..28 | 65 |
| 28 | 0..28 | 75 |
| 64 | 0..64 | 55 |
| 64 | 0..64 | 65 |
| 64 | 0..64 | 75 |

모두 m=0, join=39, orders=3, angular nodes=128, rtol=2e-11,
max_step=0.25다. 원래 atomic coordinates, B27, k7/10, E49/200Hartree,
eta_C=-10/7, H+=G+iF와 증가-r 방향 log derivative를 유지한다.

## resume와 반환

`--resume`은 동일 spec과 runtime fingerprint의 case key를 사용한다.
fingerprint는 원본 source SHA, runner CODE8개의 해시, NumPy/SciPy/mpmath
versions 및 Python build 문자열에 묶인다. 성공 영수증의 status/exit_code와
두 payload(RESULT.json,COEFFICIENTS.npz)의 해시가 모두 맞으면 재사용한다.
실패·timeout은 attempt 디렉터리에 남기며, 성공 증거가 없는 case만 새
attempt에서 실행한다. 같은 out 경로의 동시 campaign은 파일 lock이 막는다.

경로를 바꾸어도 input/runtime bytes와 spec이 같으면 같은 case key를 얻는다.
Python build·package version·구현 bytes가 바뀌면 기존 성공을 자동 재사용하지
않는다. 이번 새 profile은 PHYS64 extended18이나 smoke를 포함하지 않는다.

반환할 파일:

- `runs/phys66_longtail/SOURCE_RESULTS.zip`
- `runs/phys66_longtail/SHA256SUMS`
- `runs/phys66_longtail/PREFLIGHT.json`
- `runs/phys66_longtail/CAMPAIGN_longtail.json`

성공 시 case마다 RESULT.json, COEFFICIENTS.npz, REQUEST.json,
EXECUTION.json, stdout.txt, stderr.txt, SUCCESS.json이 묶음 안에 들어간다.
실패한 attempt와 partial campaign도 그대로 반환한다. worker가 제한시간에
걸리면 새 시간·정확도 기준을 임의로 완화하지 않고 실제 failure를 반환한다.

## 연구 상태

PHYS65/66의 해석적 radial/Born bounds는 재사용한다. 새 longtail의
integration/roundoff/angular-exclusion total error는 결과가 자체적으로
인증하지 않는다. 원래 source-driven xi와 physical cross section/rate의
완료를 이 실행으로 판정하지 않는다. **HH_R10=OFF**를 유지한다.
"""

VERIFY = r'''#!/usr/bin/env python3
"""Verify source capsule hashes without importing or executing a solver."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
manifest=json.loads((root/'MANIFEST.json').read_text())
for relative,expected in manifest['payloads'].items():
    path=(root/relative).resolve()
    if not path.is_relative_to(root):raise ValueError('invalid manifest path')
    data=path.read_bytes()
    if len(data)!=expected['bytes'] or hashlib.sha256(data).hexdigest()!=expected['sha256']:
        raise ValueError('capsule hash mismatch: '+relative)
source=manifest['frozen_source']
if hashlib.sha256((root/source['path']).read_bytes()).hexdigest()!=source['sha256']:
    raise ValueError('frozen source mismatch')
print(json.dumps({'status':'CAPSULE_HASH_VERIFIED','payloads':len(manifest['payloads']),
                  'source_sha256':source['sha256'],'solver_executed':False}))
'''

PREFLIGHT_SH = r'''#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
NCP_PYTHON="${NCP_PYTHON:-python3}"
PHYS66_RUN_OUT="${PHYS66_RUN_OUT:-runs/phys66_longtail}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
"$NCP_PYTHON" verify_capsule.py
"$NCP_PYTHON" -c 'import numpy, scipy, mpmath; print("DEPENDENCY_IMPORT_PASS", numpy.__version__, scipy.__version__, mpmath.__version__)'
exec "$NCP_PYTHON" scripts/phys66_ncp.py --profile longtail --out "$PHYS66_RUN_OUT" \
  --workers 1 --memory-gib 4 --timeout 900 --resume --preflight-only
'''

RUN_SH = PREFLIGHT_SH.replace(
    '--workers 1 --memory-gib 4 --timeout 900 --resume --preflight-only',
    '--workers 1 --memory-gib 4 --timeout 900 --resume')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(data):
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()


def zip_bytes(root, target):
    """ZIP_STORED, sorted names, fixed timestamp/perms: reproducible bytes."""
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_STORED) as archive:
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 10, 19, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (0o100755 if relative.endswith(".sh") else 0o100644) << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, path.read_bytes())


def prepare(package_dir, archive_path):
    source_hash = source_guard(REPO / SOURCE)
    files = {path: (REPO / path).read_bytes() for path in SOURCE_INPUTS}
    # Verify the direct local-import closure; no runtime-specific dependency
    # is assumed to be supplied merely because a root repository contains it.
    local_modules = {Path(p).stem for p in files if p.startswith("src/wu088_hh/")}
    for name, content in tuple(files.items()):
        if name.startswith("src/") and name.endswith(".py"):
            for node in ast.walk(ast.parse(content, name)):
                if isinstance(node, ast.ImportFrom) and node.level and node.module:
                    if node.module.split(".")[0] not in local_modules:
                        raise ValueError("missing local import dependency: " + node.module)
    specs = case_specs("longtail")
    if [(max(x["ells"]), x["outer"]) for x in specs] != [(l, float(t)) for l in (28, 64) for t in (55, 65, 75)]:
        raise ValueError("the existing longtail contract changed")
    files["requirements-pinned.txt"] = "".join(f"{k}=={v}\n" for k, v in VERSIONS.items()).encode()
    files["START_HERE_KO.md"] = README.encode()
    files["verify_capsule.py"] = VERIFY.encode()
    files["run_preflight.sh"] = PREFLIGHT_SH.encode()
    files["run_longtail.sh"] = RUN_SH.encode()
    files["REQUESTS_LONGTAIL.json"] = json_bytes({
        "schema": "PHYS66_LONGTAIL_SIX_REQUESTS_V1", "profile": "longtail",
        "request_count": len(specs), "requests": specs, "workers": 1,
        "memory_gib_per_worker": 4, "wall_seconds_per_case": 900,
        "resume": True, "submission_status": "NOT_SUBMITTED", "HH_R10": "OFF"})
    try:
        base_head = subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        base_head = None
    manifest = {
        "schema": "PHYS67_NCP_SOURCE_CAPSULE_V1", "base_repository_head": base_head,
        "base_head_scope": "repository HEAD at preparation; restored overlay is identified by payload hashes",
        "frozen_source": {"path": SOURCE, "sha256": source_hash},
        "pinned_package_versions": VERSIONS,
        "runner_fingerprint_paths": CODE,
        "payloads": {p: {"bytes": len(b), "sha256": digest(b)} for p, b in sorted(files.items())},
        "submission_status": "NOT_SUBMITTED", "scientific_case_executions_during_preparation": 0,
        "HH_R10": "OFF",
    }
    files["MANIFEST.json"] = json_bytes(manifest)
    files["SHA256SUMS"] = "".join(f"{digest(b)}  {p}\n" for p, b in sorted(files.items())).encode()
    package_dir.mkdir(parents=True, exist_ok=True)
    for name, content in sorted(files.items()):
        path = package_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != content:
            raise ValueError("existing capsule differs; choose a new empty target directory")
        path.write_bytes(content)
    actual_names = {p.relative_to(package_dir).as_posix() for p in package_dir.rglob("*") if p.is_file()}
    if actual_names != set(files):
        raise ValueError("capsule target must contain only its exact declared files")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    zip_bytes(package_dir, archive_path)
    rebuilt = archive_path.with_name(archive_path.name + ".determinism-check")
    zip_bytes(package_dir, rebuilt)
    if archive_path.read_bytes() != rebuilt.read_bytes():
        raise ValueError("archive deterministic-byte check failed")
    rebuilt.unlink()
    record = {
        "schema": "PHYS67_NCP_DELIVERY_PREPARATION_V1", "status": "PREPARED_NOT_SUBMITTED",
        "base_repository_head": base_head,
        "archive_name": archive_path.name, "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": digest(archive_path.read_bytes()),
        "deterministic_rebuild_byte_identity": True, "archive_member_count": len(files),
        "manifest_payload_count": len(manifest["payloads"]),
        "frozen_source_sha256": source_hash, "request_count": len(specs),
        "source_files": {p: digest((REPO/p).read_bytes()) for p in SOURCE_INPUTS},
        "scientific_case_executions": 0, "ncp_submission": "NOT_SUBMITTED",
        "ncp_host_preflight": "NOT_RUN", "sandbox_capsule_preflight": "PENDING",
        "package_wheels_included": False, "HH_R10": "OFF",
    }
    (Path(__file__).parent / "DELIVERY_PREPARATION.json").write_bytes(json_bytes(record))
    (Path(__file__).parent / "CAPSULE_SHA256SUMS").write_text(record["archive_sha256"]+"  "+archive_path.name+"\n")
    (Path(__file__).parent / "REQUESTS_LONGTAIL.json").write_bytes(files["REQUESTS_LONGTAIL.json"])
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.package_dir.resolve(), args.archive.resolve())
