# 전달 D — 실제 S/C/B2를 연결한 정의된 단위20/20

Actual S `a891cd4b9a3548e66db669b9eb472fea88a3b78b`, tree `ee6768ab8a934cb9b47819a24cf5498e4f8b8ece`; C `7caca70d94d03732bff5e7adf2f9aa5cf59310ec`, tree `ebeaf6623dfd0077adae43933f8494056e8974c8`. Draft PR100 <https://github.com/cosmosapjw-quantum/BASS_HE/pull/100>, merge=false/activation=false. D는 CURRENT_FILE_COMMIT이며 R10/C10 COMPLETE_AT_DELIVERY_COMMIT, 정의된 단위20/20 scoped다. 전체 HE-ANG SOURCE_INPUT_PENDING/global completion=null. 실제 E/B3의 external PR100tail은 아직 pending이다.

Actual B2 `HEANG_CBA_NORDSIECK_SCIENCE_20261025_a891cd4b_7caca70d.tar.gz`, 2054451bytes/142members; uploaded-byte SHA256 `a3525a7d739695f2755de50f761524b98190b4d7b4dbcb67392e9cd6da4c2911`; Drive `10VI1GXobkRS-r1dWrxb-_nSHjg9phvRV`, Dropbox `id:BSpOijBcT10AAAAAAD_9tg`. Exact local member verification and both providers' actual upload plus separate metadata-size ACK are confirmed. Independent remote wholeGET/SHA256 is not asserted. Contents: exactS87/C3,wholeB1once,10inheritedledgers,dependencywheel,actualpublication/correction/postSownerreceipts. Packaging CPU 0.161368652/wall 0.16143304800061742s is operational cost separate from science; other remote/provider IO remains UNKNOWN_NOT_ZERO.

# HE-ANG-CBA-NORDSIECK 실제 결과

고정핵 직접 Coulomb–Born 모형의 수소 1s overlap, delta-state 정규화와 절대 labelled TDCS를 유도하고 구현했다. 핵심 식은 THEORY_KO.md의 (1)–(9)다. 전체 HE-ANG physical provider 채택과 이번 analytic model의 확보 범위는 CLAIM_GATE.json에서 분리한다.

## 새 수학과 구현

원전 Eq19/A9의 I는 1/r 적분이다. 1s 전이 overlap K는 eta,p,q를 고정한 -partial_lambda I로 얻는다. eta=lambda/p는 그 뒤 적용한다. 이 순서에서 K(lambda,-p,p;eta)=2I0(lambda-eta*p)/(p²+lambda²)가 되어 같은 Coulomb Hamiltonian의 bound–continuum 직교성을 재현한다. Source Eq18의 추가1/r와 Appendix A7 부호는 실제 읽은 preprint의 문자적 불일치로 기록했고 출판본 교정 여부는 추정하지 않았다. 원전 Eq28의 J와 이번 K는 서로 다른 적분이다.

Matched eta=lambda/p에서 Delta=q+p로 쓰면 K=16*pi*lambda*C*[Delta²-(1+i*eta)Delta.p]/(A²*Bc)다. 작은 Delta의 두 큰 항을 빼지 않는 구현이고 Delta0은 정확히0이다. Generic overlap와 별도로 이 식을 주 경로로 사용했다. Principal Log(Bc)는 lambda,p>0에서 Im(Bc)<0인 연속 가지로 고정했다.

Nc=(2*pi)^(-3/2)exp(pi*eta/2)Gamma(1-i*eta)와 정규화된1s를 사용한 F_D에 대해 TDCS=4*(pf*p/pi_momentum)*|F_D|²/Delta^4다. Box-state 황금률/상태밀도/flux와 delta-state T 양쪽 계수를 맞췄다. 직접 spin-diagonal 채널의 spin factor는1이다. 수소 matched 경로의 nuclear overlap은0이며 eta0 plane-wave control에서는 nuclear subtraction을 유지했다. 단위 a0,p0,E_h와 물리 TDCS a0²/E_h를 명시했다.

## 실제 수치 근거

| 관측 | 범위 | 최대 관측 오차 |
|---|---|---:|
| 표적 테스트 | 14methods, failures0/errors0 | PASS |
| Generic I/K binary64 | 9inputs, mp80 reference | 1.0629567988304066e-15 scaled |
| Formula precision | 같은9inputs mp50–mp80 | 9.183265145706724e-51 scaled |
| 원적분 Eq6 quadrature | 4moderate complex cases,mp50 | 3.506764608003949e-51 scaled |
| Stable tiny transfer | 16parallel/transverse inputs | 4.0063870834280886e-16 true relative |
| Nc/Sommerfeld normalization | 7eta values | 1.5116805406513489e-15 scaled |
| Delta-state TDCS conversion | 73angles×2models | 7.159247292900658e-16 scaled |

Scaled error는 abs(value-reference)/max(1,abs(reference))이다. Tiny-transfer만 nonzero mp80 reference에 대한 true relative error를 썼다. Tolerance를 실행 뒤 바꾸지 않았다. 원적분 quadrature는 K의 parabolic-coordinate 1차원 적분이며 closed I의 수치 미분을 되풀이한 검사가 아니다.

Conditioning 예: pvec=(0,0,0.7),lambda1, transverse Delta=(1e-14,0,0)에서 generic subtraction 식의 상대오차는1.742881133761018e12, 안정식은1.928809976914049e-16이다. 같은 t의 parallel generic error는0.016729855113103972, 안정식은1.8021982992221216e-16이다. 이들은 작은-transfer 수학 fixture이며 실제 ionization kinematics에서 Delta0 사건을 의미하지 않는다. 전체 입력 공간에 대한 uniform/outward error bound는 주장하지 않는다.

Illustration은 source에서 읽은250eV incident/5eV ejected/3degree scattered geometry와 nominal U27.2를 사용했다. Oriented coplanar angle -180..180degree step5의73points에서 표본최대는 두 모형 모두 -50degree에 있다. Direct CBA0.45610407121581825, direct plane0.9421399651692766 a0²/(eV sr²)이다. 이는 새 근사의 계산 예이며 원전 곡선 fit,20/54.4/413.6eV 데이터 재적합 또는 연속각 최대치의 증명이 아니다. 그림은 저장된 JSON만 읽어 만들었다.

## 실제 실행·실패·비용

Three actual children은 tests0.2772319999999999CPU/0.3188933669953258wall, analysis2.580506/2.6289747010014253, saved-output plot2.130236/2.174621346995991초다. 합계4.987974CPU/5.122489414992742wall, 새20/60할당,512MiB/1thread다. Repair reserve1은 미사용이며 이전 예산에서 이전하지 않았다. 변경 없는 이전 suite 및 이번 tests/analysis 재실행은0이다.

첫03_plot 호출은 기존0byte RUN.lock 때문에 scientific START 전에 중단됐다. 실제02session terminalexit0,완성FINISH,관련activeprocess0,03START없음을 확인하고 원시traceback/lockstat를 보존한 뒤 그 lock만 제거했다. 이후 plot child를 처음 실제로 실행했다. Stale-lock 발생/cleanup 실패의 원인은 NOT_ESTABLISHED, prelaunch CPU는 UNKNOWN_NOT_ZERO이다. 이를 scientific child 실패나 reserve 소비로 바꾸지 않았다.

Wolfram original call은12True/5structuralFalse/1unevaluated, targeted diagnostic6residual은Together/FullSimplify/유리수대입 모두0이다. Cancel의 항별 표현을 SameQ로 literal0과 비교한 false-FAIL을 교정했으며 첫 결과를 그대로 남겼다. Evaluator2calls toolwall16.886s,bodyCPU0.304298s/bodywall0.304892s; context1call toolwall20.315s; 합toolwall37.201s다. Remote 전체CPU는 UNKNOWN_NOT_ZERO이다. Third evaluator call은 없었다. SciSpace2search,Exa2search+2fetch(4URLs)의401/timeout 및 이전403도 보존했다.

Metadata preparation0.038864099000000006CPU/0.040913912998803426wall, B1pack0.07220352099999999/0.0722468569947523초를 별도로 기록했다. 모델·provider·IO·prelaunch 및 과거unknown은0으로 환산하지 않았고 end-to-end 총 cap은 입증하지 않았다. PR99의2.484451/2.519181445000868,PR98의3.117567/3.242023329999938,PR97의3.304038/3.4507949489989187 및 모든 이전 원장·실패·reserve 상태는 inherited reference chain에 보존한다.

## 조사와 남은 의무

초기 최신 조사:7repos,14collections,30pages terminal,1339branches/874openPRs. Dropbox4929entries/9pages,Drive926documents/3pages+27folders/1page terminal이다. Drive document 검색은 binary archive 전체를 열거하지 않으므로 knownID metadata 확인과 구분한다. 관련 대화는1query-selected이며 self-echo/stale delivery 요약을 새 근거로 채택하지 않았다. 선택된 PR/원전 본문과 전체 branch metadata의 coverage를 구분한다.

중앙 HEAD는 조사 시작E9600a605에서2354d6e9로 진행했다. 게시 시점의 실제 최신 HEAD와 DAG를 사용하여 그 owner 변경과 모든 oldHE/other39를 보존한다. REC/CR/HH의 scoped 결과·OPEN·비용·실패·unknown은 해당owner 범위에 둔다. C23E 및 미래 partial mu_window theta metadata C9-NB-01도 OPEN으로 유지한다.

전체 HE-ANG은 SOURCE_INPUT_PENDING이다. 다음 실제 연구 입력은 source-consistent physical joint amplitude/event payload와 source validity, spin/exchange/count, full support, frame/finite-M dynamics, calibrated uncertainty다. 이번 fixed-centre amplitude와 PR99 finite-M shell의 결합은 그 별도 의무를 만족한 뒤 수행한다. Event sigma, physical recoil law, HE-X1 empirical angular correction을 이번 단위에서 승인하지 않았다. 새 strong no-go 또는 문헌 최초성 주장은 없다.


## 단계와 저장 상태

정의된 단위의 과학 S는18/20이다. R10/C10은 실제 S/C/B2/D/E/B3 게시·backup·전달에 연결할 pending 의무다. 전체 HE-ANG 물리 목표 달성률은 null이다. B1은 preexecution 범위의 실제 dual ACK이며 이후 결과/C9/이 문서가 B1에 담긴 것으로 쓰지 않는다. S/B2 및 전달 D/E/B3는 아직 실제 게시 영수증 대기다.

| 단계 | 이름 | 현재 상태 | 근거 |
|---|---|---|---|
| R1 | 연구 위치·계약 | COMPLETE_SCOPED | [FROZEN_CONTRACT.json](FROZEN_CONTRACT.json); [evidence/survey/AGENTS_REUSE_CHECK.json](evidence/survey/AGENTS_REUSE_CHECK.json); [evidence/survey/entry/ENTRY_PREFLIGHT.json](evidence/survey/entry/ENTRY_PREFLIGHT.json); [evidence/survey/FRESH_CENTRAL_BASE_RECEIPT.json](evidence/survey/FRESH_CENTRAL_BASE_RECEIPT.json); [evidence/survey/CENTRAL_CHANGE_OBSERVATIONS.json](evidence/survey/CENTRAL_CHANGE_OBSERVATIONS.json) |
| R2 | 근거·재사용 | COMPLETE_SCOPED | [evidence/source/SOURCE_REPORT.md](evidence/source/SOURCE_REPORT.md); [evidence/source/SOURCE_CALL_LEDGER.json](evidence/source/SOURCE_CALL_LEDGER.json); [evidence/survey/INHERITED_LEDGER_REFERENCES.json](evidence/survey/INHERITED_LEDGER_REFERENCES.json) |
| R3 | 주장·전제 정렬 | COMPLETE_SCOPED | [THEORY_KO.md](THEORY_KO.md); [FROZEN_CONTRACT.json](FROZEN_CONTRACT.json) |
| R4 | 가설·표현 탐색 | COMPLETE_SCOPED | [THEORY_KO.md](THEORY_KO.md); [evidence/source/SOURCE_REPORT.md](evidence/source/SOURCE_REPORT.md) |
| R5 | 구성적 유도 | COMPLETE_SCOPED | [THEORY_KO.md](THEORY_KO.md); [reviews/R6_REPORT.json](reviews/R6_REPORT.json) |
| R6 | 독립 검증 | COMPLETE_SCOPED | [reviews/R6_REPORT.json](reviews/R6_REPORT.json); [reviews/R6_REVIEW.md](reviews/R6_REVIEW.md) |
| R7 | 판별 검증 | COMPLETE_SCOPED | [evidence/wolfram/CBA_SYMBOLIC.wl](evidence/wolfram/CBA_SYMBOLIC.wl); [evidence/wolfram/ACTUAL_EVALUATOR_RESULT.json](evidence/wolfram/ACTUAL_EVALUATOR_RESULT.json); [evidence/wolfram/DIAGNOSTIC.wl](evidence/wolfram/DIAGNOSTIC.wl); [evidence/wolfram/ACTUAL_DIAGNOSTIC_RESULT.json](evidence/wolfram/ACTUAL_DIAGNOSTIC_RESULT.json); [reviews/R7_DIAGNOSTIC_REVIEW.json](reviews/R7_DIAGNOSTIC_REVIEW.json); [evidence/wolfram/WOLFRAM_SUMMARY.json](evidence/wolfram/WOLFRAM_SUMMARY.json) |
| R8 | 결과 판정 | COMPLETE_SCOPED | [reviews/ROOT_ADMISSION.json](reviews/ROOT_ADMISSION.json); [CLAIM_GATE.json](CLAIM_GATE.json); [RESULTS_KO.md](RESULTS_KO.md) |
| R9 | 정식 결과·코딩 연결 | COMPLETE_SCOPED | [THEORY_KO.md](THEORY_KO.md); [FROZEN_CONTRACT.json](FROZEN_CONTRACT.json); [evidence/preparation/MAPPING_DESIGN.md](evidence/preparation/MAPPING_DESIGN.md) |
| R10 | 종료·재개 | PENDING_ACTUAL_PUBLICATION | [HANDOFF_RESEARCH_KO.md](HANDOFF_RESEARCH_KO.md); [delivery/PUBLICATION.json](delivery/PUBLICATION.json); [delivery/S_PUBLICATION_RECEIPT.json](delivery/S_PUBLICATION_RECEIPT.json); [delivery/C_PUBLICATION_RECEIPT.json](delivery/C_PUBLICATION_RECEIPT.json); [delivery/B2_BACKUP_ACK.json](delivery/B2_BACKUP_ACK.json) |
| C1 | 목표·baseline | COMPLETE_SCOPED | [FROZEN_CONTRACT.json](FROZEN_CONTRACT.json); [evidence/survey/LOCAL_DURABILITY.json](evidence/survey/LOCAL_DURABILITY.json) |
| C2 | 식–데이터–코드 | COMPLETE_SCOPED | [evidence/preparation/MAPPING_DESIGN.md](evidence/preparation/MAPPING_DESIGN.md); [code/cba.py](code/cba.py) |
| C3 | 수치 설계 | COMPLETE_SCOPED | [evidence/preparation/FIXTURES.json](evidence/preparation/FIXTURES.json); [code/test_cba.py](code/test_cba.py); [code/run_analysis.py](code/run_analysis.py) |
| C4 | 실행 DAG·자원 | COMPLETE_SCOPED | [FROZEN_CONTRACT.json](FROZEN_CONTRACT.json); [evidence/preparation/HOST_RESOURCE_OBSERVATION.json](evidence/preparation/HOST_RESOURCE_OBSERVATION.json); [evidence/execution/RESOURCE_LEDGER.json](evidence/execution/RESOURCE_LEDGER.json); [delivery/B1_BACKUP_ACK.json](delivery/B1_BACKUP_ACK.json) |
| C5 | 구현 | COMPLETE_SCOPED | [code/cba.py](code/cba.py); [code/test_cba.py](code/test_cba.py); [code/run_analysis.py](code/run_analysis.py); [code/plot_results.py](code/plot_results.py); [code/run_bounded.py](code/run_bounded.py); [evidence/preparation/SYNTAX_ONLY.json](evidence/preparation/SYNTAX_ONLY.json); [evidence/execution/PRELAUNCH_03_FAILURE.json](evidence/execution/PRELAUNCH_03_FAILURE.json); [evidence/execution/PRELAUNCH_03_CLEANUP_AUTHORIZATION.json](evidence/execution/PRELAUNCH_03_CLEANUP_AUTHORIZATION.json) |
| C6 | 표적 검증 | COMPLETE_SCOPED | [results/TEST_REPORT.json](results/TEST_REPORT.json); [evidence/execution/01_01_tests/START.json](evidence/execution/01_01_tests/START.json); [evidence/execution/01_01_tests/FINISH.json](evidence/execution/01_01_tests/FINISH.json) |
| C7 | 판별 계산 | COMPLETE_SCOPED | [results/ANALYSIS.json](results/ANALYSIS.json); [evidence/execution/02_02_analysis/START.json](evidence/execution/02_02_analysis/START.json); [evidence/execution/02_02_analysis/FINISH.json](evidence/execution/02_02_analysis/FINISH.json) |
| C8 | 결과 해석·시각화 | COMPLETE_SCOPED | [results/figures/PLOT_RECEIPT.json](results/figures/PLOT_RECEIPT.json); [reviews/C9_REPORT.json](reviews/C9_REPORT.json); [results/figures/CBA_NORDSIECK.png](results/figures/CBA_NORDSIECK.png); [results/figures/CBA_NORDSIECK.svg](results/figures/CBA_NORDSIECK.svg); [evidence/execution/03_03_plot/FINISH.json](evidence/execution/03_03_plot/FINISH.json) |
| C9 | 독립 코드·결과 검토 | COMPLETE_SCOPED | [reviews/C9_REPORT.json](reviews/C9_REPORT.json); [reviews/ROOT_ADMISSION.json](reviews/ROOT_ADMISSION.json) |
| C10 | 저장·전달 | PENDING_ACTUAL_PUBLICATION | [CLAIM_GATE.json](CLAIM_GATE.json); [HANDOFF_RESEARCH_KO.md](HANDOFF_RESEARCH_KO.md); [delivery/PUBLICATION.json](delivery/PUBLICATION.json); [delivery/B2_BACKUP_ACK.json](delivery/B2_BACKUP_ACK.json) |


## 실제 S/C 및 전달 D 보충

앞의 과학 결과/18/20 표는 immutable science S의 당시 상태다. Actual S `a891cd4b9a3548e66db669b9eb472fea88a3b78b`, tree `ee6768ab8a934cb9b47819a24cf5498e4f8b8ece`; actual C `7caca70d94d03732bff5e7adf2f9aa5cf59310ec`, tree `ebeaf6623dfd0077adae43933f8494056e8974c8`이며 Draft PR100 <https://github.com/cosmosapjw-quantum/BASS_HE/pull/100>는 unmerged/activation=false다. C는 fresh b0f02efc canonical base의 모든 other39nodes/40contracts/7authorities/17edges와 oldHE를 그대로 보존하고 own cba_nordsieck_subunit만 추가했다.

S0 `86fc9206d885633b59745fb80dcc22fa163bfd89`의 CSV rawCRLF→LF publication BYTE_IDENTITY_MISMATCH를 그대로 남겼다. Successor S는 rawCSV 하나만 교정했으며 root가87/87 remote blobs/size와 다른88research trees/14rootentries 보존을 확인했다. Original S87stage/과학 code/theory/rawresults/reviews는 변하지 않았다. unit_delivery textpacket의 read_text를 read_bytes().decode로 교정했다. 과학 실패/재실행/추가C9/reserve소비는0이며 publication/provider cost는 UNKNOWN_NOT_ZERO다.

D는 실제 S/C와 B2dual actualACK가 확인된 뒤 작성되는 전달 commit이다. D자기SHA는 CURRENT_FILE_COMMIT이며 정의된 단위만20/20 scoped, R10/C10 COMPLETE_AT_DELIVERY_COMMIT이다. 실제 E/B3와 final externalPR100receipt는 대기한다. 자기 미래 SHA/ACK를 소급 삽입하지 않는다. B1은 preexecution-only, B2는 exactS/C와 실제 포장 manifest scope, D/E overlay B3는 그 실제 생성/업로드 이후 범위로 구분한다. Local archive/member verification 및 dual provider upload/metadata ACK와 독립 remote wholeGET/SHA 검증을 구분한다.

Post-S canonical change에서 CR neutral FP finite-chain과 PHYS89 covariance source diagnosis/typed finite interface는 각owner의 conditional/scoped 결과로 보존됐다. PHYS89 physicalparent PARTIAL_INPUT_DEPENDENCIES, displayed covariance stochastic admission DISALLOWED, defect cause NOT_ESTABLISHED, BASS nuclear consumer NOT_BOUND, HH_R10OFF/production NOT_ISSUED다. 이 HE worker는 owner의 보고된 wholeGET/CRC/restore를 새로 수행하지 않았다. CR fullN4/N5PARTIAL/OPEN/N6N7gated와 Driveunknown, REC227 별도관측/H5 및 C23E/C9-NB-01/allownerOPEN/costs/failures/unknown은 유지한다.

추가 운영 비용: S local assembly CPU0.04895616800000001/wall0.050382883004203904s, C assembly CPU0.050501431/wall0.05072827399999369s. B2 포장 실제 비용/ACK는 별도 root file의 실제 값을 연결한다. Scientific3children CPU4.987974/wall5.122489414992742와 Wolfram/sourcecall/priorledger 숫자를 바꾸거나 합산 총cap으로 승격하지 않는다. 전체 미측정 host/model/provider/IO/prelaunch 비용은 UNKNOWN_NOT_ZERO다.

HE-ANG SOURCE_INPUT_PENDING, physical provider/event_sigma/physical recoil/HE-X1 empirical correction=false, global completion=null을 유지한다. 현재한단위의 actualE/B3/finalPRhandoff를 닫은 뒤 중단하며 unusedreserve/newloop/merge/activation은 실행하지 않는다.


B2 actual receipt details: Actual B2 `HEANG_CBA_NORDSIECK_SCIENCE_20261025_a891cd4b_7caca70d.tar.gz`, 2054451bytes/142members; uploaded-byte SHA256 `a3525a7d739695f2755de50f761524b98190b4d7b4dbcb67392e9cd6da4c2911`; Drive `10VI1GXobkRS-r1dWrxb-_nSHjg9phvRV`, Dropbox `id:BSpOijBcT10AAAAAAD_9tg`. Exact local member verification and both providers' actual upload plus separate metadata-size ACK are confirmed. Independent remote wholeGET/SHA256 is not asserted. Contents: exactS87/C3,wholeB1once,10inheritedledgers,dependencywheel,actualpublication/correction/postSownerreceipts. Packaging CPU 0.161368652/wall 0.16143304800061742s is operational cost separate from science; other remote/provider IO remains UNKNOWN_NOT_ZERO.
