# Physmath 연구 루프 완료 대응표

이 문서는 실제 수행한 이론 R1–R10과 코딩 C1–C10을 단일 DAG의 근거에 연결한다. 동일한 source와 전제를 유지한 기존 검증은 재사용했다. 마지막 보존·게시 단계의 완료 시각, commit과 provider ACK는 FINAL_DELIVERY_ACK.json이 결정한다. 이 문서의 포장 시점보다 뒤에 생성되는 ACK는 별도 객체로 보존한다.

## 이론 연구 R1–R10

| 단계 | 실제 산출물·판정 | DAG / 근거 |
|---|---|---|
| R1 연구 위치·계약 | non-tilted LRS, 독립 matter/radiation 초기 응력, 175점과 z20→2 범위 고정. A/B/C lane 및 완료 조건 분리 | D0–D2; UNIFIED_EXECUTION_CONTRACT.md |
| R2 근거·재사용 | PR147 vendor 및 PR198 원자료, 원래 94개 회수, Exa/SciSpace 원전 발견과 원논문 확인, 35개 정확한 재사용 조건 식별 | D0–D1; PHYSICS_EVIDENCE.json; CASE_PROVENANCE_LEDGER_INDEX.json |
| R3 주장·전제 정렬 | half/Frobenius, proper-time SI 계수, signed tensor sum, 개별 reflection-even 분포와 total flux 조건 구별 | D2; PHYSICAL_CONVENTION_ADAPTER.md |
| R4 가설·표현 탐색 | 초기 total stress 상쇄 뒤의 shear 생성과 후기 turnover를 판별량으로 선택; signed component와 norm을 함께 저장 | D2–D4; NEW_SCIENTIFIC_RESULTS_KO.md |
| R5 구성적 유도 | Einstein/shear/conservation 식 대응, 초기 상쇄 조건에서 S_F''(0)=−(1−B_m)P_m,i 유도; B_m의 pressure-weighted velocity 식 제시 | D2; PHYSICAL_CONVENTION_ADAPTER.md; cancellation_curvature_check.json |
| R6 독립 검증 | 실제 Wolfram 기호 검산, 별도 검토자의 물리 계약 심사와 유도/해석 심사 | D2/D5; PHYS_MATH_CONTRACT_REVIEW.json; independent_audit/D7_INTERPRETATION_REVIEW.json |
| R7 판별 검증 | 누락된 143개 초기 구간 및 237개 tail 완료; 보존 raw로 초기 상쇄·후기 turnover·4개 late sign reversal 판별 | D3–D4; B1/B2 CHECK.json; NEW_SCIENTIFIC_EVIDENCE.json |
| R8 결과 판정 | 제한 모형의 국소 유도와 유한 grid 수치 결과를 채택. PR198 preliminary PASS 및 AGE HOLD 유지 | D5; UNIFIED_STATUS.md; independent_audit/ |
| R9 정식 결과·코딩 연결 | 식–함수–단위–closure–입력축 대응 및 실제 그림/CSV와 실행 source-file SHA를 연결 | D2–D5; PHYSICAL_CONVENTION_ADAPTER.md; ledger; PLOT_MANIFEST.json |
| R10 종료·재개 | saved histories의 cancellation_turnover 노드 0 IVP로 완료. 다음 단일 노드는 네 late reversal의 저장 sample bracket 산출 | D7/D8; UNIFIED_DAG.json; CODEX_HANDOFF.md; NEXT_THREAD_HANDOFF.md; FINAL_DELIVERY_ACK.json |

## 코딩 연구 C1–C10

| 단계 | 실제 산출물·판정 | DAG / 근거 |
|---|---|---|
| C1 목표·baseline | 기존 625+606, 91+3, 175 계약 및 AGE history 구분. 현재 runtime Python/C++ 실제 실행 확인 | D0–D1; evidence/CURRENT_RUNTIME.json; UNIFIED_STATUS.md |
| C2 식–데이터–코드 | canonical FV massive moment, radiation hierarchy, cosmology lock, adapter와 full-state continuation 경로 확인 | D2; convention adapter; source manifests |
| C3 수치 설계 | 기존 DOP853/허용오차·quadrature 유지. independent IVP 병렬화, worker cache, bounded diagnostic vectorization, hash-bound reference 재사용 | D2; OPTIMIZATION_RESEARCH_KO.md; UNIFIED_EXECUTION_CONTRACT.md |
| C4 실행 DAG·자원 | 실제 로컬 quota 안에서 4 또는 2 workers, inner threads 1, 누적 child/controller 예산 유지. NCP 현재 미관측을 분리 | D2–D3; resources.py; runtime/phase receipts |
| C5 구현 | 140개 누락 nominal+3 guards, 237개 endpoint full-state tail, 성분별 13종 그림과 CSV 생성 경로 완성 | D3–D4; components/; z2_extension/ |
| C6 구현 검증 | 첫 100개 tail 저장 후 NumPy boolean receipt 직렬화 실패를 보존. bool 변환과 data-only recovery로 해결하고 137개 미실행만 진행 | D3; OPERATIONAL_REPAIR_AUTHORIZATION.json; OPERATIONAL_REPAIR_REVIEW.json |
| C7 과학 검증 | constraint, signed stress, species work, 실현 초기축, 분포 positivity, exact prefix/join을 실제 raw와 대조 | D3/D5; B1_RAW_AUDIT.json; B2_FINAL_RAW_AUDIT.json |
| C8 수치·재현성 | 3개 신규 초기 구간 및 6개 tail refinement guards PASS, 실제 source/config/raw hash와 실패/복구 provenance 보존 | D3; CHECK.json; CASE_PROVENANCE_LEDGER_INDEX.json |
| C9 독립 검토 | PHYS-MATH→CODE/raw→실제 그림 검토. 잘린 label과 history 축/endpoint 표시를 수정한 최종 PNG를 재검토 | D5; independent_audit/; ROOT_FIGURE_REVIEW.json |
| C10 판정·인계 | 소유 경로에 additive expected-head FF, 전체 Git readback, create-only Drive/Dropbox archive와 전체 GET/bytes/SHA, 복사 가능한 인계 | D6–D7; PUBLICATION_RECEIPT.json; FINAL_DELIVERY_ACK.json; handoffs |

## 근거 등급과 연구 판단

- **literature-supported:** reflection symmetry와 collisionless Bianchi kinetic 구조, massive/massless redshifting의 구별. 원전별 범위는 PHYSICS_EVIDENCE.json에 기록했다.
- **derived:** 정규화·차원·tensor sum 대응, 초기 상쇄에서의 국소 shear 곡률, signed shear evolution과 damping/source balance.
- **implementation-verified:** source pin, worker별 immutable setup reuse, full-state restart, case checkpoint, thread/resource admission, plotting input receipt/hash gating.
- **numerically checked:** 저장된 175점, 237개 unique z20→2 histories, 지정된 refinement controls, cancellation과 late sign reversals.
- **unresolved / blocked:** NCP 현재 hardware·checkout 상태와 실제 NCP 실행. 로컬 실행 결과 및 원자료는 이미 확보했다.
- **unresolved:** AGE native time convergence 및 nonlinear Grackle response bound. 기존 HOLD 판정을 변경하지 않았다.
- **conjectural:** 연속 parameter space의 zero-crossing surface나 보편적인 endpoint response 법칙은 이번 결과에 포함하지 않는다.

새로운 strong no-go 정리는 채택하지 않았다. 초기 total stress=0 조건의 두 실제 trajectory와 국소 유도는 그 조건에서의 후속 shear 생성을 보여 준다. NG1–NG7의 일반 배제 정리·새로운 문헌상 우선권을 주장하지 않는다. 정확히 닫힌 수치/해석 검토는 재개 시 유지하고, 새로운 조건 또는 material discrepancy의 의존성만 다시 연다.

## 단계별 보존 원칙

D0–D2는 복구 checkpoint와 문서 commit으로 보존했다. D3는 별도 실행 archive에 모든 완료/실패 raw·receipt·수리 전후 source를 담아 양쪽 provider의 전체 파일을 회수했다. D4–D7은 최종 source/results commit과 최종 archive, 그 이후의 publication ACK로 닫는다. 단계별 실제 commit/provider/검증 상태는 UNIFIED_DAG.json과 FINAL_DELIVERY_ACK.json을 따른다.

