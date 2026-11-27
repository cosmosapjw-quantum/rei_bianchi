# B1 저장 결과 재사용과 새 출력 재현

이 문서는 현재 완료한 실행을 자동 재시작하는 지시가 아니다. 기본 작업은 저장된
결과·판정의 재사용이다. 아래 명령은 full backup packet의 루트, 즉
`b1_transport.py`, `inputs/`, `runs/`, `analysis/`, `review/`가 있는 디렉터리에서 시작한다.
문서 작성 중 아래 환경 설치·재분석·수송 명령을 새로 실행하지 않았다.

**최상위 후속 계획:** [replan/ACTIVE_DAG.json](replan/ACTIVE_DAG.json),
[replan/DEVELOPMENT_PLAN_KO.md](replan/DEVELOPMENT_PLAN_KO.md),
[replan/NCP_LOCAL_CODEX_HANDOFF_KO.md](replan/NCP_LOCAL_CODEX_HANDOFF_KO.md)를 따른다.
기존 [NCP_LOCAL_CODEX_HANDOFF_KO.md](NCP_LOCAL_CODEX_HANDOFF_KO.md)는 리뷰된 B1 실행 종료
기록으로 보존한다. 다음 일정에서는 새 replan overlay가 우선하지만 B1 과학·판정·실패
영수증은 그대로 유지한다. 새 계획을 반영하기 위해 원본 결과를 재실행하지 않는다.

## 1. 자료의 범위와 완료 상태

현재 과학 판정은 [review/DECISION.json](review/DECISION.json)의
`PROMOTE_SCOPED_PYTHON`이다. original native gate는 `HOLD_RUNTIME_ENVIRONMENT`,
native parity는 `NOT_RUN`이다. 현재 B1 상태는 [CURRENT_STATE.json](CURRENT_STATE.json),
게시·백업 identity는 [PUBLICATION.json](PUBLICATION.json)과 최종 전달 영수증을 따른다.
상태·게시 파일은 마감 때 생성하는 포인터이며 임의의 PR/백업 ID를 추정하지 않는다.

Git dossier에는 큰 원본 NPZ와 실행 결과 전체가 빠질 수 있다. 저장된 전체 결과를
다시 분석하려면 full packet의 다음 자료를 사용한다.

- `inputs/research/broad_history_20261010/evidence/RUN002/flrw_n16384/history.npz`
- 같은 경로의 `rp01_n16384/history.npz`와 각 원래 `COMPLETE.json`
- RUN002의 `flrw_BASS_CELLS.csv`, `rp01_BASS_CELLS.csv`
- `inputs/B1_FROZEN_PROJECTED_INPUTS.npz`
- `runs/`의 13개 `result.npz`와 각 `RECEIPT.json`
- `execution_logs/RUN001/CAMPAIGN.json`
- `source_notes/HISTORY_PROJECTION_VALIDATION.json`
- `review/B1_ACTUAL_ORACLE_COMPARISON.json`
- 실행·분석 소스와 원래 `native/upstream_polarization.py`

원래 전자 이력 자체를 다시 적분하거나 30 MB C02B 또는 별도 E13 archive를
재복원해야 하는 절차가 아니다. packet manifest와 입력 manifest에 명시된 선택 payload를 재사용한다.

## 2. 환경과 스레드

기준 실행 환경을 재현하려면 **CPython 3.12.14**에 다음 버전을 사용한다.

```text
numpy==2.3.5
scipy==1.17.0
matplotlib==3.10.8
```

환경 준비가 필요한 경우에만 전용 가상환경에서 설치한다. `python3.12`가 실제
3.12.14 interpreter를 가리키는지는 사용 환경에서 확인한다. CPython 버전 선택은
pip의 라이브러리 버전 고정으로 대신되지 않는다.

```bash
python3.12 -m venv .venv-b1
source .venv-b1/bin/activate
python -c 'import sys; assert sys.version_info[:3] == (3, 12, 14), sys.version'
python -m pip install numpy==2.3.5 scipy==1.17.0 matplotlib==3.10.8
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export B1_PACKET_ROOT="$PWD"
```

이 설정은 64개 worker를 시작하는 지시가 아니다. 실제 원래 campaign은 독립 case
3개를 동시에 실행했고 과학 worker당 BLAS/OpenMP/MKL thread는 1개였다.
CPU·OS·수학 라이브러리가 달라지면 동일 source/input이라도 실수 결과의 마지막 자리나
실행시간·RSS가 달라질 수 있다. 새 실행 영수증으로 기록하며 기존 영수증을 새 환경의
실행 증거로 사용하지 않는다.

## 3. 기본 경로: 기존 결과 읽기

읽을 결과는 `REPORT_KO.md`, `figures/B1_overview.pdf`,
`analysis/B1_REPORT_POINTS.csv`, `analysis/B1_FINAL_COMPARISON.csv`,
`analysis/B1_HISTORY_RESPONSE.csv`, `analysis/B1_NUMERICAL_ASSESSMENT.json`이다.
이 자료를 읽는 데 solver 실행은 필요 없다.

그림만 다시 생성하려면 저장된 12개 base/refinement NPZ에서 별도 폴더로 출력한다.
아래 `B1_REPLOT_DIR`는 존재하지 않는 새 경로로 정한다.

```bash
export B1_REPLOT_DIR="${B1_PACKET_ROOT}_replot_01"
mkdir "$B1_REPLOT_DIR"
python "$B1_PACKET_ROOT/figures/make_figures.py" \
  --runs "$B1_PACKET_ROOT/runs" \
  --output-dir "$B1_REPLOT_DIR"
```

이 스크립트는 각 NPZ를 해당 실행 영수증의 SHA와 대조하고 그림만 출력한다.
새 광자 수송·재이온화 ODE·충돌 호출을 수행하지 않는다.

## 4. 저장된 13개 결과의 재분석을 새 경로에 남기기

`analyze_b1.py`는 CLI 출력 경로 옵션 없이 자신의 위치 아래 `analysis/`에 쓴다.
따라서 원래 dossier에서 그대로 호출하면 저장된 분석 파일을 다시 쓰게 된다.
원본을 보존하며 재분석하려면 분석 script를 새 작업 폴더에 복사하고 원래 읽기 자료만
연결한다. 아래는 Linux에서의 구체적인 방법이다. `B1_REANALYSIS_DIR`는 새 이름으로 정한다.

```bash
export B1_REANALYSIS_DIR="${B1_PACKET_ROOT}_reanalysis_01"
python - <<'PY'
import os
import shutil
from pathlib import Path

src = Path(os.environ['B1_PACKET_ROOT']).resolve()
dst = Path(os.environ['B1_REANALYSIS_DIR']).resolve()
dst.mkdir(parents=False, exist_ok=False)
for filename in ['analyze_b1.py', 'b1_transport.py']:
    shutil.copy2(src / filename, dst / filename)
for name in ['runs', 'inputs', 'native', 'execution_logs', 'source_notes', 'review']:
    (dst / name).symlink_to(src / name, target_is_directory=True)
PY
python "$B1_REANALYSIS_DIR/analyze_b1.py" \
  > "$B1_REANALYSIS_DIR/reanalysis.stdout.txt" \
  2> "$B1_REANALYSIS_DIR/reanalysis.stderr.txt"
```

새 `analysis/` 아래에 비교 CSV·NPZ·assessment·run index가 생성된다. 기존 13개
수송 결과와 기존 oracle·projection·campaign 영수증을 읽어 분석한 것이며, 그 실행을
새로 수행한 것은 아니다. 새 assessment의 runtime은 재분석 환경이고 compute에 인용하는
실행시간은 원래 보존한 수송 영수증의 값이다.

`analyze_b1.py`의 owner 상태 문자열은 검토 전 proposal을 그대로 재현한다.
따라서 재생성된 `OWNER_PROPOSED_PROMOTE_SCOPED_PYTHON_PENDING_INDEPENDENT_DECISION`을
독립 검토가 사라졌다는 뜻으로 읽거나 기존 [review/DECISION.json](review/DECISION.json)을
덮어쓰지 않는다. 최종 scoped 채택은 기존 독립 결정이 별도로 소유한다.

## 5. 입력 재투영만 다시 계산할 필요가 생긴 경우

일반 재현은 포함된 `B1_FROZEN_PROJECTED_INPUTS.npz`를 그대로 사용한다. 새 입력 비교를
위해 투영을 재계산해야 한다면 원본 Q-cell measure와 같은 midpoint H를 사용해 새 파일에 쓴다.

```bash
python "$B1_PACKET_ROOT/inputs/project_frozen_histories.py" \
  --output "$B1_REANALYSIS_DIR/B1_FROZEN_PROJECTED_INPUTS_RECOMPUTED.npz"
```

원래 F 이력을 B clock에 처방할 때의 관계는
`depth_F_on_B = depth_F * H_F_mid/H_B_mid`이며, `depth_F`에는 기존 BASS/REI Thomson
상수비가 이미 들어 있다. 이는 frozen Q-cell measure의 재가중이지 ODE 재실행이나
N4 셀 평균을 순간 밀도로 복사하는 과정이 아니다. 기존 driver의 입력 경로는
`inputs/B1_FROZEN_PROJECTED_INPUTS.npz`로 고정돼 있다. 새 파일을 만들었다고 driver가
자동으로 바뀐 입력을 사용하는 것은 아니며 기존 원본을 조용히 교체하지 않는다.

## 6. 선택적 새 수송 재현: 독립 fresh output

아래는 재실행 자체가 필요하다고 결정한 경우의 명령이다. 현재 완료 결과를 읽는
기본 경로에는 포함되지 않는다. 새 결과는 기존 `runs/`와 다른 경로에 기록한다.
`b1_transport.py --out` 대상은 아직 존재하지 않아야 하며, 폴더가 이미 있으면
`exist_ok=False`로 종료한다. 실패를 지우거나 같은 출력으로 자동 재시도하지 않는다.

```bash
export B1_FRESH_RUN_ROOT="${B1_PACKET_ROOT}_fresh_runs_01"
mkdir "$B1_FRESH_RUN_ROOT"
python "$B1_PACKET_ROOT/b1_transport.py" \
  --case B --nsteps 128 --nmu 24 --nenergy 257 \
  --log-min -8 --log-max 5 \
  --out "$B1_FRESH_RUN_ROOT/base_B_t128_mu24_e257" \
  > "$B1_FRESH_RUN_ROOT/base_B.stdout.txt" \
  2> "$B1_FRESH_RUN_ROOT/base_B.stderr.txt"
```

그 실행만으로 B_F 또는 다른 대조군이 실행됐다고 판단하지 않는다.
동일한 13개 구성 전체를 새로 재현하려면 아래 별도 fresh 경로에서 직접 driver를 호출한다.
위 단일 B 예제와 같은 출력 폴더를 재사용하지 않는다.

| Group | Cases | Time steps | GL mu | Base energy nodes |
|---|---|---:|---:|---:|
| pilot | B | 64 | 16 | 129 |
| base | F, M, B, B0, B_F, M_F | 128 | 24 | 257 |
| time | B, B_F | 256 | 24 | 257 |
| angle | B, B_F | 128 | 48 | 257 |
| energy | B, B_F | 128 | 24 | 513 |

에너지 격자는 `ln y in [-8,5]`이며 여섯 보고 에너지 `y=.1,.3,1,3,6,10`을 추가한다.
예를 들어 base 257은 actual 263 nodes다. phi 수는 현재 driver의 8로 고정돼 있다.
물리 해석을 한정한 energy guard는 y in [.1,10]이다.

```bash
export B1_FRESH_RUN_ROOT="${B1_PACKET_ROOT}_fresh_all13_01"
mkdir "$B1_FRESH_RUN_ROOT"
set -euo pipefail
run_b1_case() {
  local group="$1" case_name="$2" nt="$3" nm="$4" ne="$5"
  local label="${group}_${case_name}_t${nt}_mu${nm}_e${ne}"
  python "$B1_PACKET_ROOT/b1_transport.py" \
    --case "$case_name" --nsteps "$nt" --nmu "$nm" --nenergy "$ne" \
    --log-min -8 --log-max 5 \
    --out "$B1_FRESH_RUN_ROOT/$label" \
    > "$B1_FRESH_RUN_ROOT/${label}.stdout.txt" \
    2> "$B1_FRESH_RUN_ROOT/${label}.stderr.txt"
}
run_b1_case pilot B 64 16 129
for case_name in F M B B0 B_F M_F; do
  run_b1_case base "$case_name" 128 24 257
done
for case_name in B B_F; do
  run_b1_case time "$case_name" 256 24 257
  run_b1_case angle "$case_name" 128 48 257
  run_b1_case energy "$case_name" 128 24 513
done
```

명령은 순차적인 독립 재현이다. 원래 campaign의 3-way 동시 실행시간을 이 재현에
그대로 붙이지 않는다. 새 `RECEIPT.json`의 source/input/output identity, exit와 wall/CPU/RSS가
새 실행의 근거다. 마지막 단계가 끝난 뒤 새 결과만 그림으로 보고 싶다면 다음처럼 지정한다.

```bash
python "$B1_PACKET_ROOT/figures/make_figures.py" \
  --runs "$B1_FRESH_RUN_ROOT" \
  --output-dir "${B1_FRESH_RUN_ROOT}_figures"
```

새 실행 세트에 `analyze_b1.py`를 적용하려면 새 세트에 대응하는 campaign·oracle·입력
영수증의 귀속을 먼저 구분해야 한다. 원래 `CAMPAIGN.json`을 복사해서 새 실행의
wall time·성능 증거로 사용할 수 없다. 위 명령은 개별 새 실행 영수증을 만들지만
새로운 독립 채택 결정이나 전체 validation suite 실행을 자동으로 만들지는 않는다.

## 7. 기존 suite 재시작과 runtime 경계

`run_b1_suite.py`는 출력이 고정된 12-job driver다. 시작할 때
`execution_logs/RUN001`을 `exist_ok=False`로 만들고 `runs/base_*`, `runs/time_*`,
`runs/angle_*`, `runs/energy_*`를 사용한다. full packet에는 이 완료 기록이 이미
존재하므로 원래 위치에서 재호출하면 충돌한다. 이것은 resume 실패를 수리하라는
신호가 아니라 완료 증거를 보호하는 동작이다. 별도 새 출력 재현은 위 직접 driver 명령을 쓴다.

현재 구현은 `native/python_thomson.py`를 통해 원래 BASS Python `collide`를 실제 호출한다.
`native/`에 Rust source/binding이 포함돼 있어도 빌드·parity가 실행됐다는 뜻은 아니다.
원래 Rust 환경 실패는 `source_notes/native_environment_failure.json`에 있고,
native 완성은 `HOLD_RUNTIME_ENVIRONMENT`로 남는다. Python 재현 성공으로 이 상태를 승격하지 않는다.

이 문서는 새로운 NCP allocation을 요청하지 않는다. 현재 NCP work list는 빈 배열이다.
다음 작업 선택은 `replan/ACTIVE_DAG.json`과 새 replan handoff를 따른다.
새 과학 질문과 실제 긴 미완료 병렬 작업이 명시된 packet이 생기기 전까지
짧은 실행·분석·빌드 확인을 위해 64코어/128 GB 계산을 시작하지 않는다.
