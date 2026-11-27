# NCP 인계: 네 기준해를 먼저, VigilODE는 조건부 한 건

이 문서는 실행 가능한 코드의 인계다. 이 대화에서 NCP에 제출하거나 실행을 시작한 상태가 아니다. Remote Desktop Commander의 월간 quota 응답은 재시도·재연결을 금지했다. 접근 가능한 실행자는 현재 프로세스와 결과부터 확인하고 중복 없이 진행한다. 사용자에게 수동 다운로드·업로드를 요구하지 않는다.

## 1. 먼저 실제 반환 분석

현재 PR78과 백업에서 새 HE29 기준해를 찾으면 source/binary/table identity와 완료된 쌍을 읽고 저장된 결과부터 분석한다. 네 쌍은 m8/GL4/q0의 (r2,512),(r4,512),(r8,512),(r4,1024), 각 Radau+DOP853이다. 기존 transport 6개와 HE29 50개 source-only 검증을 반복하지 않는다. 부분 완료가 있으면 이미 완료된 case를 재실행하지 않는다.

원래 baseline 실행 명령·입력 자동 복원·native compile·6점 qualification·process group 제한은 상위 `../CODEX_HANDOFF_PROMPT_KO.md`를 따른다. 과학 source는 1569에 고정하고, 일괄 pytest 한 줄을 생략하는 기존 pinned overlay만 적용한다. S2 미게시 복구는 완료되어 있으므로 `PUBLISH.sh`를 사용하지 않는다.

## 2. publication checkout와 원래 실행 결과 연결

상위 handoff의 초기 shell에서 `HE29_STAGE`, `HE29_PUBLICATION_REV`, `HE29_REL`, `HE29_WORK_ROOT`를 기록한다. 네 쌍의 완료·admission을 먼저 확인한다. 같은 새 isolated checkout에서 baseline 실행을 완료한 경우, 다음은 입력 DATA와 알려진 bootstrap overlay를 유지한 채 고정된 새 구현 commit으로 돌아오는 절차다. 기존 사용자 작업 폴더에 적용하지 않는다.

```bash
set -euo pipefail
cd "$HE29_STAGE/BASS_HE"
HE29_PY="${HE29_PYTHON:-python3}"
if [[ -x "$HE29_WORK_ROOT/venv/bin/python" ]]; then
  HE29_PY="$HE29_WORK_ROOT/venv/bin/python"
fi
"$HE29_PY" "$HE29_REL/src/analyze_references.py" \
  --root "$HE29_WORK_ROOT/references" \
  --out "$HE29_WORK_ROOT/PRE_VIGILODE_ANALYSIS_$(date -u +%Y%m%dT%H%M%SZ).json"
HE29_VIGILODE_CODE_REV=57642252991b5c453db66eb5a078e6a62cc6f4ea
git checkout --detach "$HE29_VIGILODE_CODE_REV"
HE29_LANE="$PWD/$HE29_REL/vigilode_20261019"
[[ -f "$HE29_LANE/ncp/build_bridge.py" ]]
"$HE29_PY" "$HE29_REL/ncp/RESTORE_VERIFIED_INPUTS.py"
```

분석기는 incomplete 결과를 보존하고 exit 1을 반환하므로 `set -euo pipefail` 아래에서는 다음 단계로 가지 않는다. 다른 기존 완료 baseline을 사용하는 경우 그 결과 root와 정확한 Python 환경을 연결한다. 새 checkout에 DATA가 없다면 이미 고정된 `RESTORE_VERIFIED_INPUTS.py --archive <verified original archive>`로 22개 DATA만 복원한다. 이를 위해 baseline `START_REFERENCES.sh`를 다시 호출하지 않는다.

최신 게시·백업 receipt가 기록된 후속 문서 commit과 위 실제 실행 source commit을 구별한다. 추가 source 수정이 필요하면 diff와 수정 commit 및 새 compiler/library 정체성을 보존하고, 기존 scientific source와 gate는 그대로 유지한다.

## 3. 고정 VigilODE bridge만 컴파일

VigilODE source는 a21d573980f66fe02891bd216153443b5352f921, Rust는 1.94.1이다. 새 source는 Git에서 받는다. 보존 archive에서 source를 선택해 실행하지 않는다. 기존 환경에 같은 Git checkout와 Cargo cache가 있으면 `--vigilode-checkout <clean exact checkout> --offline`을 사용할 수 있다.

```bash
HE29_VBUILD="$HE29_WORK_ROOT/VIGILODE_BUILD_$(date -u +%Y%m%dT%H%M%SZ)"
"$HE29_PY" "$HE29_LANE/ncp/build_bridge.py" --out "$HE29_VBUILD"
```

필요하면 `--rustc /absolute/path/rustc --cargo /absolute/path/cargo`를 명시한다. wrapper는 비우고 Cargo encoded rustflags도 빈 값으로 명시해 다른 fast-math 설정을 들여오지 않는다. source/staged-copy/clean dependency의 빌드 전후 정체성을 확인한다. 실패하면 첫 `BUILD_FAILURE.json` 및 commands 로그를 보존하고 작은 환경·빌드 수정만 수행한다. 물리식·허용치·새 solver 개발로 범위를 확장하지 않는다.

## 4. preflight와 단일 r4/table512 canary

```bash
HE29_VCHECK="$HE29_WORK_ROOT/VIGILODE_PREFLIGHT_$(date -u +%Y%m%dT%H%M%SZ)"
"$HE29_PY" "$HE29_LANE/src/run_vigilode.py" preflight \
  --out "$HE29_VCHECK" \
  --baseline-campaign "$HE29_WORK_ROOT/references" \
  --binary "$HE29_WORK_ROOT/build/he29_owner_server" \
  --owner-receipt "$HE29_WORK_ROOT/build/RECEIPT.json" \
  --library "$HE29_VBUILD/target/release/libhe29_vigilode_bridge.so" \
  --bridge-receipt "$HE29_VBUILD/BUILD_IDENTITY.json"

HE29_VRUN="$HE29_WORK_ROOT/VIGILODE_CANARY_$(date -u +%Y%m%dT%H%M%SZ)"
"$HE29_PY" "$HE29_LANE/src/run_vigilode.py" canary \
  --out "$HE29_VRUN" --wall-s 900 \
  --baseline-campaign "$HE29_WORK_ROOT/references" \
  --binary "$HE29_WORK_ROOT/build/he29_owner_server" \
  --owner-receipt "$HE29_WORK_ROOT/build/RECEIPT.json" \
  --library "$HE29_VBUILD/target/release/libhe29_vigilode_bridge.so" \
  --bridge-receipt "$HE29_VBUILD/BUILD_IDENTITY.json"
```

canary는 선행 네 쌍의 완료, source/input/binary/runtime 정체성, 재생성 table SHA를 확인한다. native owner의 6점 qualification은 동일 binary bytes인 baseline 결과를 재사용한다. 새 solver의 output을 원래 photon/energy/species ledger와 Radau/DOP853 양쪽의 absolute gate로 판정한다. 시간 상한 기본 900초·최대 3600초, source table 600초·예상 allocation 2GiB, 수치 thread와 Rayon은 1이다. 실패하면 raw endpoint·마지막 완료 구간·부분 관측·native JSONL·process receipt부터 분석한다. 성공으로 덮어쓰거나 자동 격자 확장을 하지 않는다.

여기서 이미 끝낸 Rust 3개 smoke와 Python 96개 검증은 보존 receipt를 재사용한다. NCP가 바이너리를 새로 빌드한 뒤 필요한 ABI smoke만 환경 확인 목적으로 선택할 수 있으며, 이를 HE29 scientific case로 집계하지 않는다. 기존 HE28/HE29 또는 VigilODE 전체 test/benchmark suite를 다시 돌리지 않는다.

## 5. 반환·게시·백업

새 baseline 결과와 canary 결과를 서로 구별한다. 성공·실패 모두 source publication HEAD, 원래1569 및 owner f7830e2 identity, VigilODE a21d, Cargo.lock·compiler·library SHA, 모든 process/partial/ledger/table/native 로그를 보존한다. 이 optional canary는 baseline pair 완료 수를 늘리지 않는다. 새 결과는 별도 results branch/Draft PR 및 Drive/Dropbox create-only archive에 게시한다. 원본 archive c47c5efc와 798afac1은 불변으로 유지한다.

실제 DAG, 제출·시작·완료 여부, archive SHA/size, provider object ID, provider content_hash, raw-byte readback을 각각 기록한다. NCP 작업은 접수되었다는 증거가 있을 때만 SUBMITTED로 바꾼다. 연속 스펙트럼·전체 EoR·전역 gasT bound·upstream Grackle 전체 동등성·관측 Bianchi/CMB는 계속 HOLD다.
