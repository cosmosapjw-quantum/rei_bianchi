# HE30 C9 독립 변경 코드 검토

판정: **PASS_SCOPED_CHANGED_CODE_REVIEW**. 현재 완료 D3 소비 경로에서 게시를 막는 구체적인 finding은 **0개**다. 이 판정은 아래 네 파일의 정확한 bytes와 현재 compact 자료에 적용한다.

담당 `/root/backup_context`는 이 네 구현·테스트 파일을 작성하거나 수정하지 않았다. 검토는 한 번의 static changed-surface 읽기와 한 번의 좁은 read-only compact catalogue/완료 영수증 확인으로 끝냈다. 새 worker·IVP·ODE·benchmark·타 process signal은 모두 0이다. 원래 full raw와 물리 모형의 전수 감사는 반복하지 않았다.

## 검토한 source identity

| 파일 | bytes | SHA-256 |
|---|---:|---|
| `src/analyze_saved.py` | 20085 | `c32620222f95a8a6a33d029f1e9c9ee1d866efdb98073f35c6dd6ba58f19c16a` |
| `src/continuation.py` | 3507 | `b008c60139e08c189bda1b917745a5fbd19970c58db5fb597dbba442dcf8ee48` |
| `src/shared_runner.py` | 20314 | `0b5e4aa0fb125da4c23ac8dfac0c318b00fcb45ea3f9dc957b04f01cf7e5cbca` |
| `tests/test_runner.py` | 6812 | `d20e1f6190b18e2a8888bbef639db48dbf5596974a4d1ce6f02c5b52e37519cd` |

위 source hash는 검토 종료 직전에 다시 대조하여 읽은 동안 변경되지 않았음을 확인했다. 기계 판독 기록은 `CHANGED_CODE_REVIEW.json`이다.

## 확인한 변경면

| 항목 | 판정 | 실제 근거 |
|---|---|---|
| 입력과 소비 identity | PASS_SCOPED | `extract`의 source commit/vendor·raw/tail/prefix 해시, 전체 상태/common grid 확인과 `catalogue`의 compact hash/index 결합, exact member receipt를 읽었다. Archive identity 자체는 이미 검증한 restore/authority 기록에 연결된다. |
| 실제 237개와 zero-matter 축 | PASS | 237 unique, 175 joint, 91 radiation baseline, 6 guard와 joint Cartesian grid를 명시적으로 확인한다. 원래 schema의 없는 P_m_i는 0, P_r_i는 Pi_F_signed_i로 보완한다. 현재 compact readback은 237 unique / 6 guard / zero-matter 94행(guard 3개 포함)이다. |
| partial·실패 결과 보존 | PASS_SCOPED | case receipt는 완전 일치해야 재사용된다. 다른 local 결과, invalid registry, 이전 실패/partial attempt는 보존 상태로 분류한다. case/attempt immutable 기록은 `os.link`의 no-replace semantics를 쓰며, 갱신 가능한 run report/registry pointer와 구분된다. consumer는 원본 full raw를 읽기로만 연다. |
| CPU와 case lease | PASS_SCOPED | global identity lock과 기존 `cpu_<id>.lock`의 nonblocking flock을 사용한다. 하나가 busy여도 다른 case를 계속 살핀다. Popen에 CPU/case descriptor를 넘겨 coordinator 종료 후에도 child 생존 동안 lease가 유지된다. |
| 동시 작업·가용 자원 | PASS_SCOPED | affinity, cgroup quota/실제 quota headroom, 실제 CPU activity와 가용 RAM을 반영한다. max64 및 reserve와 신규 admission을 구분하고, MemAvailable에 이미 반영된 active RAM을 다시 빼지 않는다. 다른 세션이 있다는 이유만으로 전체 HOLD를 만들지 않는다. |
| 타 process signal | PASS_SCOPED | `active`에는 이 coordinator가 직접 만든 Popen만 들어가고 terminate/kill도 이 객체들에만 수행된다. 외부 process 발견 목록이나 process-name kill 경로가 없다. |
| 내부 thread 제한 | PASS_SCOPED | OMP/OpenBLAS/MKL/BLIS/NumExpr/VECLIB/Rayon=1, nested OpenMP disabled. runner와 worker는 API import 전에 이 환경을 설정하고 Popen에 전달하며, child affinity를 지정한다. |
| 현재 pending=0 | PASS | 아래의 한 번의 compact/receipt 확인에서 REUSED_COMPLETE 237, pending 0. 기존 actual RUNNER_REPORT도 worker_starts 0, pending [], active [], other_jobs_signalled 0이다. |
| 기존 targeted tests 재사용 | PASS_REUSED | 8-test PASS receipt의 shared_runner/test_runner SHA가 위 source와 정확히 일치한다. unchanged 테스트를 다시 돌리지 않았다. |

## 현재 경로의 작은 확인

현재 `continuation.case_grid()`와 `shared_runner.classify()`를 compact product 및 local 완료 영수증에만 적용했다. `runner.run()`이나 worker launch를 호출하지 않았으며, 원래 full raw를 다시 읽거나 모델·solver를 import하지 않았다.

```json
{
  "cases": 237,
  "unique_ids": 237,
  "guards": 6,
  "zero_matter_rows_including_guards": 94,
  "classification_counts": {"REUSED_COMPLETE": 237},
  "pending": 0,
  "new_worker_starts": 0,
  "new_science_runs": 0
}
```

기존 parent 실행 receipt `results/cases/RUNNER_REPORT.json`의 campaign은 `20261021T111338_cb0184da0da7`이다. `final=true`, `worker_starts=0`, `pending=[]`, `active=[]`, `other_jobs_signalled=0`이고 237개 전부 REUSED_COMPLETE다.

기존 `RUNNER_CHECK.json`은 8 PASS를 기록한다. 3개의 fixture child는 파일 I/O 성공 2개와 의도적 실패 1개이며 과학 계산이 아니다. 동일 source 해시를 확인했으므로 이 bounded correctness 근거를 재사용한다. 0.417초는 해당 검사 실행 기록이며 성능 개선 배율의 근거가 아니다.

## 종료와 결합 범위

추가 수정이나 새 검토 cycle을 요구하는 현재 blocking finding은 없다. parent는 이 기록을 C9 근거로 결합하고 기존 물리 결과 검토·그림 검토·게시·백업을 각자의 근거로 완료하면 된다. 이 코드 검토가 원래 D3 전체 과학 검증, 실제 NCP scaling 측정, Git 게시 또는 원격 backup ACK를 대신하지는 않는다.
