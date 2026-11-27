# B1 — 처방된 전자 이력과 편광 광자 수송

**판정: `PROMOTE_SCOPED_PYTHON`.** 원래의 native Rust B1 연결은
`HOLD_RUNTIME_ENVIRONMENT`, Python–Rust parity는 `NOT_RUN`이다.
이번 dossier는 기존 frozen 전자 이력과 기존 BASS Python Thomson 구현으로
실제로 계산한 LRS Bianchi I test-field 결과를 제공한다.
[독립 결정](review/DECISION.json)과 [검토문](review/DECISION_REVIEW_KO.md)이 채택 범위의 권위다.

**다음 연구 일정과 우선순위는 새 재편 overlay를 먼저 따른다:**
[replan/ACTIVE_DAG.json](replan/ACTIVE_DAG.json),
[replan/DEVELOPMENT_PLAN_KO.md](replan/DEVELOPMENT_PLAN_KO.md),
[replan/NCP_LOCAL_CODEX_HANDOFF_KO.md](replan/NCP_LOCAL_CODEX_HANDOFF_KO.md).
사용자가 새로 제공한 DAG의 반영은 후속 계획을 바꾸는 것이며, 아래 B1의 원본 과학 결과와
독립 판정을 수정하거나 완료 실행을 재시작하는 근거가 아니다.

## 먼저 읽을 파일

- [REPORT_KO.md](REPORT_KO.md): 질문, 유도, 실제 결과와 해석.
- [SCIENTIFIC_CONTRACT.md](SCIENTIFIC_CONTRACT.md): 단위·초기조건·비교 조건과 보호할 의미.
- [CURRENT_STATE.json](CURRENT_STATE.json): B1 마감 상태. 후속 일정은 위 replan overlay가 우선.
- [analysis/B1_NUMERICAL_ASSESSMENT.json](analysis/B1_NUMERICAL_ASSESSMENT.json): 수치 비교·실행 집계.
- [figures/B1_overview.pdf](figures/B1_overview.pdf): 네 패널의 과학 그림.
- [REPRODUCTION_KO.md](REPRODUCTION_KO.md): 저장 결과 재분석과 선택적인 새 출력 재현 방법.
- [NCP_LOCAL_CODEX_HANDOFF_KO.md](NCP_LOCAL_CODEX_HANDOFF_KO.md): 리뷰된 B1 실행 종료 기록.
  다음 일정·이관은 [새 replan handoff](replan/NCP_LOCAL_CODEX_HANDOFF_KO.md)를 따른다.

게시 commit/PR와 백업 포인터는 마감 시 생성하는 [PUBLICATION.json](PUBLICATION.json)과
최종 전달 영수증을 따른다. 이 README는 원격 게시·백업의 성공 응답을 대신하지 않는다.

## 실제 계산과 과학적 범위

기준 실행 F/M/B/B0/B_F/M_F 6개, 시간·각도·에너지 refinement 6개, pilot 1개를
완료했다. 모든 실행은 새 출력에 기록됐다. 기존 reduced-history ODE 재실행 0,
native Rust 실행 0, NCP 실행 0이다. 각 실제 실행은
`runs/<run_name>/{result.npz,observables.csv,RECEIPT.json,RUN_STATE.json}`으로 보존된다.

전자 이력은 기존 R15/HG97-B의 FLRW와 초기 s/H=+0.1 자료이며, 평균 부피 z=20→4,
고정 ionized-zone gas T=20000 K, C_HII=3, HII+HeII closure다. 방향 수송의 초기조건은
기존 BASS benchmark에서 사용한 등방·비편광 Planck 형태이며 이후 photon emissivity는 0이다.
원래 유효 이온화 광자 방출률에서 복사 스펙트럼을 추론하지 않았다.

| Case | Geometry | Electron history / clock |
|---|---|---|
| F | FLRW | F history / F clock |
| M | B와 같은 mean H의 등방 대조군 | B history / B clock |
| B | LRS Bianchi I | B history / B clock |
| B0 | B와 동일 | 충돌 깊이 0 / B clock |
| B_F | B와 동일 | F history / B clock |
| M_F | M과 동일 | F history / B clock |

주 반응은 정규화된 사중극 q2 및 `(B−M)−(B_F−M_F)`이고 선형 편광도를 함께 기록했다.
에너지는 `y=(a/a_i)E/(k_B T_gamma,i)`로 표시한다. 이 y는 공변 운동량 방향별 slice가
아니며, 같은 시각에 모든 방향의 같은 물리 에너지를 뜻한다. T_gamma,i는 benchmark
에너지 척도이며 가스 온도와 다르다.

격자 refinement와 null floor는 이번 실행에서 관측한 수치 민감도다. 엄밀 enclosure,
전체 물리 오차, 통계 신뢰구간은 아니다. observer tail, 관측 적색편이 변환,
전체 CMB optical depth, 관측 CMB C_l, 실제 ionizing spectrum·gas feedback은 이 결과에 없다.

## Git dossier와 full backup packet

**Git만 받은 경우:** 작은 보고서·코드·판정·CSV 요약·그림 등 dossier subset이 게시될 수 있다.
원래 dense NPZ와 13개 실행의 큰 result NPZ/CSV가 없으면 전체 재분석에 필요한 입력이
충족되지 않은 것이다. Git 파일 목록만으로 원시 결과가 복구됐다고 판단하지 않는다.

**Full packet을 받은 경우:** `inputs/`의 선택 원본 두 history, N4 셀과 projection,
`runs/`의 13개 실제 실행, `analysis/`, `review/`, `execution_logs/`, `source_notes/`,
`figures/`와 실행 코드를 함께 사용한다. 원래 30 MB C02B archive 전체나 E13의 별도
대형 archive를 다시 풀 필요는 없다. 포함한 선택 입력의 provenance는
[B1_HISTORY_INPUT_MANIFEST.json](source_notes/B1_HISTORY_INPUT_MANIFEST.json)에 있다.

기본 경로는 **이미 저장된 보고서·그림·CSV를 읽고 필요하면 저장된 NPZ를 재분석하는 것**이다.
`run_b1_suite.py`는 현재 완료 실행을 이어받는 resume 명령이 아니다. 기존
`execution_logs/RUN001` 또는 같은 run 출력이 있으면 새 생성 보호로 종료하므로,
완료 기록을 삭제해서 재실행하지 않는다. 별도 재현이 필요한 경우에만
[REPRODUCTION_KO.md](REPRODUCTION_KO.md)의 새 출력 명령을 사용한다.

## 실행 환경

실제 기준 환경은 **CPython 3.12.14, NumPy 2.3.5, SciPy 1.17.0,
Matplotlib 3.10.8**이다. 과학 worker당 `OPENBLAS_NUM_THREADS=1`,
`OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`을 사용했다.
충돌 backend는 `EXPLICIT_EXISTING_BASS_PYTHON`이며
`native/upstream_polarization.py`의 원래 `collide`를 호출한다.
폴더 이름 `native/`만으로 Rust 실행을 의미하지 않는다.

Rust compiler/prebuilt library 부재와 compiler 취득 실패는
[native_environment_failure.json](source_notes/native_environment_failure.json)에 보존했다.
Python의 scoped 성공을 native 성공으로 변경하지 않는다.
현재 새 NCP work unit은 `[]`다. B1 종료 시점의 E13C11 대기 기록은 보존하고,
후속 노드 선택과 일정은 새 replan overlay에서 결정한다.
