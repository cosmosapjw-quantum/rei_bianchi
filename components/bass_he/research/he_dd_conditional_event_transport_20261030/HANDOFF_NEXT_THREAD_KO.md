# BASS_HE | 조건부 330-MeV 단면적과 쌍생성 비열평형 연결부 인계

```ini
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
IMMUTABLE_PARENT_PR=113
IMMUTABLE_PARENT_HEAD=da989b83bb37ee4256a1a80ba9400dfe48559084
GRANDPARENT_PR=112
GRANDPARENT_HEAD=a03c1eee365c9b796fef137b81a4347ad44008d1
CONTINUATION_BRANCH=research/he-dd-conditional-event-transport-20261030
CONTINUATION_PR=READ_CURRENT_REMOTE
CONTINUATION_HEAD=READ_CURRENT_REMOTE
CONTINUATION_ROOT=research/he_dd_conditional_event_transport_20261030
CENTRAL_DAG=28/88
HE_DAG=14/18
MEASURED_DATA_DAG=2/2_SCOPED
PHYSICAL_DELTA=0
THEORY_WORKFLOW=9/10_FROM_PARENT_PR113_UNCHANGED
CODING_WORKFLOW=9/10_FROM_PARENT_PR113_UNCHANGED
INDEPENDENT_R6_C9=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
kappa=null
R_event=null
heat_rate=null
physical_activation=false
L4=false
production=HOLD
```

## Provenance와 재개 순서

1. PR113 및 PR112 HEAD와 새로운 Draft descendant PR/HEAD를 GitHub에서 실측한다. 원 부모 SHA가 변했다면 덮어쓰지 않고 분기·계보를 보존한다.
2. 원본 EXFOR `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4` (3349 bytes, SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, Git blob `c49433293921dbb012d7f1b0387745732a598efa`)와 PR113 compact measured atlas Git blob `293cb5d6937cf6c84584cb8d6f0a37336f50535f`를 원형 유지한다.
3. 새 ROOT/{THEORY_KO.md,src/he_dd_conditional_bridge.py,tests/test_he_dd_conditional_bridge.py,results/RESULTS_CONDITIONAL_330.json}를 읽는다.
4. 조건부 330 MeV 보간은 측정 SIG가 아니다. `sigma_reported_lin=773/1300 nb`, 독립 오차 SD `0.125036746735462 nb`, 알려지지 않은 상관에서 SD `[157/1950, 307/1950] nb`, C² 가정 시 미확정 체계오차 `-145 MeV² sigma''(xi)`다. 실측 단면적은 320/359 MeV만 존재한다. `sigma_event_330`는 NULL이며, 열 주입률도 NULL이다.
5. 구별 가능한 실험 검출기 arm 대신 동일한 두 D의 상관된 사건(두 4-운동량)을 생성한다. 시험에서 `N_D,event=2`, `K_pair=E_gamma-Q`, 모든 물리 보존량을 확인한다. `dσ_event/dΩ`의 event/inclusive 보정, 검출 효율, 편광은 직접 원전 확인 전까지 미확정이다.
6. EXFOR source exact atlas를 다운받아 Git blob을 검사한 다음 `python -m unittest discover -s tests -p 'test_*.py' -q`, `python -m compileall -q src tests`, `python src/he_dd_conditional_bridge.py --atlas ../he_dd_exfor_measured_kinetic_atlas_20261029/results/MEASURED_KINETIC_COORDINATES.json`를 새 ROOT에서 실행한다. 마지막 원본 atlas end-to-end 명령은 이번 런타임에서 NOT_RUN. 전체 과거 IVP나 4501-node LP는 반복하지 않는다.
7. 다음 정규 물리 경로: Arends1976/Silverman1984 full original methods detector acceptance/efficiency/polarization/event counting; 독립적 330 MeV event sigma 또는 명시적 모델·모델오차의 물리 유효성; MeV photon history n_gamma^(alpha)(E,Ω,x), He 타깃 proper distribution; 이름 있는 D_fast stopping/redistribution/escape kernel, ionization/secondary energy and C_V; 그 후 테스트와 DAG admission.

## 실제 이번 단계 구현·검증

- 새 `src/he_dd_conditional_bridge.py`: frozen atlas Git blob fail-closed 검사, 무측정 보간, 모든 daughter 쌍에 대한 4-vector, 보존법칙.
- `tests/test_he_dd_conditional_bridge.py`: 현재 런타임 Python 3.13의 focused 8/8 PASS, compileall PASS, 12 실제 DA 좌표×2 azimuths에 대해 daughter number, 4-momentum, mass shell, exchange symmetry, out-of-range guard.
- Wolfram exact 검산: Q, threshold, 보간 추정량, 통계 오차 극값, 에너지와 z 모멘텀 합.
- Arends full detector methods는 이번 세션에서 미획득; 실험 기하·효율로부터 kappa를 계산했다고 주장하지 않는다.
- Native independent reviewer 불가: R6/C9 distinct-author NOT_RUN. 부모 DAG와 production HOLD 유지.
- 원인 구별: `physical_input_missing`, `original_paper_access_limited`, `native_subagent_unavailable`, `independent_review_not_run`; 수학적 mass-shell failure는 관측되지 않음.

## 백업 계약

- 이론/코드/테스트/결과의 Git blob을 실제로 재조회해 로컬 byte SHA와 비교한다. Git stage commit은 `STAGE_RECEIPTS.json`에서 확인한다.
- Google Docs/Dropbox Paper 내용 읽기 ACK는 text backup일 뿐 ZIP byte ACK/복원은 별개다. README/manifest와 ZIP CRC, 원본 소스 해시를 확인한 뒤에만 full binary restored라 표기한다.
- Draft PR merge/force push, 기존 물리 DAG 승격, production activation 금지.
