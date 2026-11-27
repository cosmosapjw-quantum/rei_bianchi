# R1–R10 / C1–C10 실제 근거표

불변 science S는 `9fc8185437f145a6ba4569e1b38aa2e12d15acd9`/draft PR101이며 당시 완료17/20이다. C46a102b22b54cc03a91ad92bbd58d68dd82b7964의 실제 게시/readback과 B2 dual ACK를 확보하여 R10/C10을 D 전달 스냅샷에서 닫는19/20 준비가 완료됐다. 아래 표는 실제 receipt를 근거로 하며 문서 생성 자체를 새 과학 단계로 세지 않는다. C8은 PARTIAL_EXPORT로 남는다. D own SHA와 E/B3/final tail은 게시 뒤 external actual receipt에서 확정한다.

| 단계 | 현재 실제 상태 | 근거 | 범위와 남은 의무 |
|---|---|---|---|
| R1 연구 위치·계약 | COMPLETE | `FROZEN_CONTRACT.json`; `CONTRACT_ADDENDUM_01.json`; `evidence/survey/SURVEY_REPORT.md` | Parent99/100, plain snapshot 및 source/claim 경계 고정 |
| R2 근거·재사용 | COMPLETE | `evidence/source/SOURCE_REPORT.md`; `evidence/source/SOURCE_CALL_LEDGER.json`; `evidence/INHERITED_LEDGER_REFERENCES.json` | 실제 primary intake와 기존 HE/DDCS20/source/원장 재사용; old suite replay 없음 |
| R3 주장·전제 정렬 | COMPLETE | `THEORY_KO.md`; `CLAIM_GATE.json` | Labelled direct C1 closure; physical provider false |
| R4 가설·표현 탐색 | COMPLETE | `THEORY_KO.md` 식(3)–(9); `FROZEN_CONTRACT.json` | 같은 Hamiltonian에서 두 recoil Fourier phase와 reduced-mass matching 선택 |
| R5 구성적 유도 | COMPLETE | `THEORY_KO.md` 식(1)–(14) | Canonical separation, W/flux, Jacobi/lab density, weighted-fold bridge |
| R6 독립 검증 | COMPLETE | `reviews/R6_REPORT.json`; `reviews/R6_REVIEW.md` | 독립 scoped PASS; authoritative theory20ff0760…; source PNG 실제 검토 |
| R7 판별 검증 | COMPLETE | `evidence/wolfram/ACTUAL_RESULT.json`; `evidence/wolfram/WOLFRAM_SUMMARY.json`; `reviews/R7_REVIEW.json` | One evaluator23True/23zero; Infinity message/origin NOT_ISOLATED 보존, 별도 exact rational proof; 추가 evaluator 없음 |
| R8 결과 판정 | COMPLETE | `RESULTS_KO.md`; `RESULT_SUMMARY.json`; `reviews/ROOT_ADMISSION.json` | Saved finite numerical/PNG scoped 채택, 두 실제 process FAIL과 C8 OPEN 유지 |
| R9 정식 결과·코딩 연결 | COMPLETE | `THEORY_KO.md`; `FROZEN_CONTRACT.json`; `CONTRACT_ADDENDUM_01.json` | 식–API–고정 fixture–측도 연결; no physical promotion |
| R10 종료·재개 | COMPLETE_AT_D_DELIVERY_SNAPSHOT | `HANDOFF_RESEARCH_KO.md`; actual S/C receipts; `delivery/B2_BACKUP_ACK.json`; `delivery/PUBLICATION.json` | 실제 S/C/B2 근거로 D19/20 전달 준비; D own SHA 및 E/B3/final actual tail은 외부 receipt에서 기록 |
| C1 목표·baseline | COMPLETE | `FROZEN_CONTRACT.json`; `evidence/recovery/PARENT_D_COPY_VERIFICATION.json` | BaseD8e0fb28…와 parent module identities 고정 |
| C2 식–데이터–코드 | COMPLETE | `THEORY_KO.md`; `code/fm_cba.py`; `code/reference.py` | 두 phase overlap, 원 K 적분, 단위·spin/count·Er label 연결 |
| C3 수치 설계 | COMPLETE | `FROZEN_CONTRACT.json`; `reviews/PRESTART_ROOT_DISPOSITION.json` | 오차 정의·고정 tolerances·fixture counts; finite-M surrogate criterion과 평가오차 구별 |
| C4 실행 DAG·자원 | COMPLETE | `FROZEN_CONTRACT.json`; `REPAIR_CONTRACT_01.json`; `evidence/execution/ROOT_GO.json`; `evidence/execution/ROOT_REPAIR_GO.json` | 원12/35 및 lineage20/60 유지; diagnosed single reserve 사용 |
| C5 구현 | COMPLETE | 원7code; `code/resume_analysis_repair01.py`; `code/run_repair01.py`; `reviews/C9_STATIC_REVIEW.json` | Parent byte unchanged, preSTART 두 static fix 및 별도 reviewed continuation |
| C6 구현 검증 | COMPLETE | `results/TEST_REPORT.json`; `evidence/execution/01_01_tests/FINISH.json` |17methods/0failures/0errors, actual PASS, 재실행 없음 |
| C7 과학 검증 | COMPLETE | `results/ANALYSIS.json`; `RESULT_SUMMARY.json`; `reviews/C9_REPORT.json` |12generic/3quad×2terms/12tiny/4kin/3fold/73angles/8trend; fixed finite numerical PASS |
| C8 수치·재현성 | IN_PROGRESS / PARTIAL_EXPORT | `results/ANALYSIS.json`; `results/figures/FINITE_M_CBA.png`; `evidence/execution/03_REPAIR01_COMBINED/FINISH.json`; C9-EXPORT-01 | SVG/producer FIGURE_METADATA/original REPAIR01_SUMMARY 없음; actual FAIL 유지, reserve0, retry 승인 없음 |
| C9 독립 검토 | COMPLETE | `reviews/C9_REPORT.json`; `reviews/C9_REVIEW.md`; `reviews/ROOT_ADMISSION.json` | PASS_SCOPED_NUMERICAL_WITH_FAILED_PROCESSES_AND_PARTIAL_EXPORT; 실제 PNG 검토 |
| C10 판정·인계 | COMPLETE_AT_D_DELIVERY_SNAPSHOT | `reviews/ROOT_ADMISSION.json`; actual S/C receipts; `delivery/B2_BACKUP_ACK.json`; `delivery/FINAL_BACKUP_ACK.json` | 실제 근거에 따른19/20, C8 OPEN; D own SHA와 E/B3 future ACK를 self-reference로 조작하지 않음 |

## 단계 수와 비용의 해석

불변 S의 COMPLETE는17개다. 실제 S/C/B2 근거로 R10/C10을 닫는 D 전달 스냅샷은19개이며 C8은 OPEN으로 남는다. 이것은 정의된 연구 단위의 stage 수이며 전체 HE-ANG 물리 목표의 완료율이 아니다. Global completion은null이다.

Actual attempts는 PASS/FAIL/FAIL, exit0/-9/-9다. 새 science11.882829CPU/11.985978921002243wall under12/35, parent 포함 lineage16.870803CPU/17.108468335994985wall under20/60이다. Per-child overshoot와 두 FAIL을 지우지 않는다. Reserve1사용/0잔여이며 parent reserve와 모든 이전 비용·실패·unknown은 비양도다. 준비·backup·provider·도구 wall과 remote/model/IO unknown은 science 합계에0으로 넣지 않으며 end-to-end cap을 주장하지 않는다.

첫 별도 물리 입력은 HE-ANG-SOURCE-PAYLOAD다. C9-NB-01 미래 partial mu_window metadata, C23E 및 다른 owner OPEN은 현재 stage 수나 finite-M direct 모형 확보로 닫히지 않는다. 다음 계산·새 node·budget reset·merge/activation은 승인되지 않았다.
