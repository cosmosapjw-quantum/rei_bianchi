# 현재 상태 — NCP 반환 완료, 2026-10-20T110800Z

상태 갱신: 2026-10-20T17:20:33Z. 실행 source **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**, VigilODE pin **8a8bd409b1d96c7b7421f496d229e119fd3d284e**의 실제 NCP 결과를 회수했다. metadata intake HEAD는 **90c46b3d305ae7d1c3a6d54cd5de6b55dfdc70ec**이며 실행 source와 구분한다.

Locked release build exit 0 (345.147809 s), Rust 4 unit + 6 integration = **10 PASS**, 기존 **cell-cache 19설정(10 Radau + 9 SSPRK 대조) 모두 완료**다. 누적 RHS 시도 38,840, raw 내부 경과시간 합계 4.937230308 s다. `cell-borrowed` fixed Radau N2의 exit 0과 유한 물리값 일치가 반환됐다. 이 대화의 새 native 실행·build는 각각 **0**이며 저장된 반환 증거를 분석한다.

NCP binary SHA256은 **c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992**다. 이전 C10 sandbox binary `3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a`와 다른 실행 산출물이다. borrowed 개별 argv·inputs receipt·outcome receipt·binary hash는 archive에 없다. 동일 binary 연결은 delivery의 진술이며 독립 borrowed receipt로 복원되지 않는다. 명령을 추정하지 않으며 이 제한만으로 native 재실행을 의무화하지 않는다.

N2의 RHS 395·cell preparations 2,680·node visits 252,800은 같고 지정 상태/node clone은 cache 338/216,320 대 borrowed 0/0이다. raw wall은 cache 0.041180299 s, borrowed 0.061808789 s이며 stderr 마지막 0.091509 s는 측정 경계가 다르다. **speedup·memory reduction은 NOT_ESTABLISHED**, default legacy·성능 경로와 batch cell-cache는 유지한다. source-on 일반2차·uniform stiff·일반 양수성·Case B/full EoR/signed Bianchi·넓은 positive-CMB/비영 boundary·continuous global certificate는 HOLD, production은 NOT_ISSUED다.

archive `REI_LRS_V14_CACHE_BORROWED_NCP_20261020T110800Z.tar.gz`: 47,372,583 bytes, SHA256 `b1cb2ce21c14626794c69585822a29ed016206769ec1dd217ae59ec3f70f53bd`. 이전에 게시된 이 archive의 양쪽 full readback receipt와 이번 회수 증거를 구분한다. 저장소 CI 두 job의 cargo fmt 실패·cargo test skipped도 NCP 표적시험 PASS와 별개다.

다음 행동은 반환 결과를 사용하고, 실제 profile이 병목을 보일 때 후속 optimizer 하나만 선택하는 것이다. 완료된 build·19설정·N2 smoke를 강제로 반복하지 않는다. 이번의 승인 범위는 ADMIT_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT이며, 독립 판정 PASS_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT와 함께 반환 분석 STATE와 review/에 기록했다.

[반환 분석](ncp_return_analysis_20261020/REPORT_KO.md), [상태](ncp_return_analysis_20261020/STATE.json), [다음 대화](NEXT_THREAD_PROMPT_KO.md)를 먼저 읽는다.

---

## 보존한 C10 기록 — 2026-10-20 07:39 UTC 상태

아래 NOT_RUN은 당시 시점에만 적용한다. 아래 실행 명령은 보존된 선택적 재현 절차이며 완료된 NCP 작업을 재실행하라는 지시가 아니다. borrowed 실제 argv를 이 명령으로 대체하지 않는다.

# 독립 LRS — borrowed-cell 연구 결과와 전달
작성: 2026-10-20 UTC. 연구 단위: continuation_20261020b.

## 결론
**동일 node 연산열을 유지하면서 지정된 cached 상태·node 복사를 제거했다. 기존 fixture의 수치 동등성은 통과했지만 속도 향상은 입증되지 않았다.** 최종 v2는 명시적 cell-borrowed 실험 옵션으로 게시한다. 성능 목적의 기존 cell-cache와 default legacy를 유지한다. 추가 SIMD, 내부 병렬 reduction, solver 변경은 이 결과에 포함하지 않는다.

최종 실행 source는 **5248822167e3fbe374f4333f7f2efdcdbfdaeeaf**, 실행 binary SHA256은 **3eeda61b64529a83b2604b6e08d448e5b11f067a81faf70bd12509076dde106a**다. source commit과 이후 전달 메타데이터 commit을 구분한다. [소스](https://github.com/cosmosapjw-quantum/rei_bianchi/commit/5248822167e3fbe374f4333f7f2efdcdbfdaeeaf), [독립 C9 판정](review/C9_VERDICT.json), [root 판정](ROOT_ADMISSION.json), [소스 변화](SOURCE_DELTA.json)를 함께 읽는다.

## 1. 연구 전에 확인한 새 실행
직전 전달 HEAD 70a9ff3f2437101a1df13054dcb10f8106741b26 및 2026-10-20 06:22:26 UTC를 기준으로 원문 조회를 수행했다. PR198 HEAD는 intake 시점에 그대로였고 이전 실제 code source는 33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1이었다.

| 확인 범위 | 실제 확인과 이번 LRS에 대한 의미 |
|---|---|
| Drive 필수 트리 | 39개 폴더, 187개 고유 항목 중 파일149·하위폴더38. cutoff 이후 생성/수정 후보0. 폴더별 최대18개로 조회 상한100에 닿지 않았다. |
| 인접 Drive rei_bianchi_research_backups | 119개 파일, 하위폴더0, cutoff 이후 후보0. |
| Dropbox rei_bianchi 전체 | recursive46항목, has_more=false, cutoff 이후 후보0. |
| 다른 대화 | 대화 검색 오류. 반환 파일은 04시대의 과거 결과여서 최신 실행 근거로 채택하지 않았다. 모든 대화 검색 성공을 주장하지 않는다. |
| VigilODE PR77 | 실제 실행 source49ca3150c68d527a275c855ecf814122ff9c533a, exit0, test stdout, AUDIT/RESULTS/PREFLIGHT를 읽었다. 별도 reaction–diffusion 모델이다. 실패 source와 exit101도 보존했다. |
| rei RUN19 | sourcef2996d02908e5a2e678fab0dc0efb3424fa86a99, COMMAND exit0와47,630byte stdout. 72조건×5반복의 instantaneous gas RHS, ivps=0. |
| rec_bianchi PR110 | 실제 sourcee2b39e33e7c840fbe63024bf9e918ef5a1bfaf6d, exit0,14,667byte stdout,16step smoke. SMOKE_ONLY/HOLD_CAP_BEFORE_RT_BOUNDARY/REI_activation=false 유지. |
| PR199·BASS_HE PR78 | 새 문서/receipt는 읽었지만 해당 작업의 새 native 완료를 확인하지 못했다. 각각의 PENDING/HOLD를 유지했다. |
| WU088_HH PR120 | 기존03:02 실행 sample의 실제 returncode0·RESULT·빈 stderr 확인. 다른 HH 모델의 SIMD/구조 solve 증거다. |

VigilODE main/최근30 Actions/PR73–77 및 지정 인접 저장소를 확인했다. rei_flrw·rei_r9 API404와 owner-wide search 빈 결과는 접근/발견 범위의 제한으로 기록했다. 범위 밖까지 모든 저장소를 확인했다고 쓰지 않는다. 세부 query·raw 응답·실제 source/receipt 연결은 [intake 요약](intake/upstream/FINDINGS_KO.md)과 [백업 intake](intake/backups/BACKUP_INTAKE_KO.md), 최종 백업의 전체 intake 원문에 있다.

PR198 CI의 여섯 실제 job은 같은 기존 native workspace의 cargo fmt --check에서 exit1이었다. timestamp prefix만 제거한 실패 step의225,974byte SHA가 모두 c7beacbb028116d61616c371e95600a3277a1dee5eba818c2ece811995559a46로 같았고 cargo test는 skipped였다. 이는 이번 adapter 실행의 PASS/FAIL 증거로 쓸 수 없다. 범위 밖15파일의 formatting 변경을 이 연구에 섞지 않았다. [실제 CI 기록](intake/ci/CI_INTAKE_SUMMARY.json)

새 source524882의 두 CI run39385516271·39385511196도 실제 job steps를 다시 읽었다. 두 job 모두 cargo fmt 단계에서 실패했고 cargo test는 skipped였다. [현재 source CI 원문](CURRENT_SOURCE_CI.json)에 별도로 보존했으며 이 기록은 archive 포장 뒤 확인한 최종 metadata다.

## 2. 식에서 구현으로
광자 상태 p=(N,U,lo,hi), Context에서 고정된 ray scale r_i, 원본 셀 준비 함수 Q_i를 둔다. 광자 좌표 하나가 바뀌면 해당 셀 k만 원본 prepare_cell로 재구성하고, 나머지 셀은 base의 준비 결과를 빌려 쓴다. 기체 좌표 섭동이면 변경 셀이 없다.

\[
\mathcal N(p;k)=\bigoplus_{i=0}^{C-1}
\begin{cases}Q_i(p,r_i),&i=k,\\Q_i(p_0,r_i),&i\ne k.\end{cases}
\]

이 연결은 셀 오름차순·셀 내부 원래 node 순서다. 현재 셀 길이 m_i에 대해 node j의 평탄 위치는 \(j+\sum_{h<i}m_h\)다. 빈 셀과 길이가 바뀐 replacement도 같은 대응을 따른다.

기존 결과·보정 변수 전체를 S_l, 원래 node 연산을 Φ로 두면 \(S_{l+1}=\Phi(S_l,\nu_l)\)이다. 복사한 node와 빌린 node가 같은 값·같은 순서이고 같은 초기 상태와 Φ를 공유하므로 귀납적으로 연산열이 유지된다. 합산을 재배열해 같은 합만 얻는 논증을 사용하지 않는다. 종 순서, 곱셈 결합, photo/binding/heat 누적, 세 compensated_add의 순서를 그대로 보존했다.

원본 native_rates는 V14 추가 모듈 안에 있었다. 따라서 이를 같은 추가 모듈의 공통 iterator helper로 추출했고, 원본 native152개 파일의 기존 바이트와 기존 append hook을 바꾸지 않았다. NativeBorrowedView는 cache·현재 state를 불변 참조하고 변경 셀의 PreparedCell 하나를 소유한다. shape→changed 범위→support/미변경 셀 stale→replacement 준비의 오류 순서와 diagnostics 병합도 유지했다.

기존 Vec의 값을 빌리는 Rust Iterator API를 사용하므로 새 dependency는 필요하지 않았다. 실제 회수한 [Rust flat_map 공식 문서](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.flat_map)와 [Vec 문서](https://doc.rust-lang.org/std/vec/struct.Vec.html)를 근거로 타입/소유권 경계를 정했다. v1에서 가속을 확인하지 못한 후, [for_each 공식 문서](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.for_each)의 내부 순회 설명에 따라 바깥 for만 for_each로 바꾸는 v2 한 번을 승인했다. closure 안의 산술은 동일하다. 문서가 성능을 보증한다고 해석하지 않았다.

셀 수 C, 현재 node 수 M, node 크기 S일 때 제거 대상의 논리 payload는 평가당 \(4C\,\mathrm{sizeof}(f64)+MS\)다. 전체 중앙차분이 허용되는 d차원 Jacobian에서 상태 복사는1+2d회였고, 각 섭동의 node 수가 같을 때 node 복사는(1+2d)M개였다. 변경 셀 node 수가 바뀌는 일반식과 귀납법은 [전체 이론 기록](THEORY_AND_SCOPE_KO.md)에 있다. Wolfram에서 empty/ragged/replacement의 비가환 symbolic fold와 비용식의 환원을 실제 실행했다. 같은 순서의 두 symbolic 상태식은True, replacement를 끝으로 옮긴 반례는False였다. 이것은 작은 기호 확인이며 native 이력이나 시간 정확도 실험으로 집계하지 않는다.

total-H 기준의 e=x+Y(y+2z), Y=.2454/[4(1-.2454)] 및 P/C/R/D·binding/heat/cooling/escape/CMB/work 분리는 유지했다. 이전 에너지 항등식·선형GL2 차수·제조76문제·Python57은 변경되지 않은 근거로 재사용하며 새 성과 수에 더하지 않는다.

## 3. 실제 코드·검증 범위
정상 Git 수정 파일은 native_additions/axbi_native_rhs.rs, src/lib.rs, src/main.rs, prepare_and_run.py다. CLI에 cell-borrowed를 추가하고 비교 경로를 보존했다. 비용 계수는 cached_prepared_state_clones와 cached_prepared_node_clones로 좁게 명명했다.

| 확인 | 실제 결과 |
|---|---|
| v1 locked/offline release build | exit0,17.751초 |
| v2 locked/offline release build | exit0,17.790초 |
| Rust 표적시험 | 각 버전4 unit+6 integration, 총10개 PASS. 기존 suite를 새 모드까지 확장한 것이며 새20개 고유 시험으로 세지 않는다. |
| changed-path 회귀 | seeded/empty/delta full-J, threshold/steep replacement와 node 수 변화, diagnostics, stale/support/shape/index, cap·transaction·domain/fatal 확인 |
| 기존19설정 재현 | 각 버전10 Radau+9 SSPRK 회귀 대조 모두 완료. 동일한 기존 fixture 반복이다. |
| 독립 전체 raw 읽기 | C9가 버전당60개 raw, 공유 숫자2,272,828·기타360·container174,120 대조. 차이0·metadata issue0. signed-zero 비트 검사는 아님. |
| Python 실행기 | 기존4개 실제 PASS. v2에서는 runner source 불변을 확인해 결과 재사용. |
| 정상 복원 | prepare-only exit0. native153(추가 모듈 포함)/adapter7/VigilODE477이 실제 compiled source와 일치. |
| 옵션 전달 smoke | 정상 runner의 run_cases를 통해 실제 fixed RadauN2 실행, CellBorrowed·exit0·공유 물리 값 일치. prepare-only와 빌드는 별도로 검증했다. |
| 실행 예산 | 두 버전의 case subprocess 관측 wall 합계53.148715초(프로파일·smoke 포함), 계약180초 이내. 컴파일 시간과 시험 executable 시간은 이 case 합계의 정의에 포함하지 않는다. |

VigilODE pin8a8bd409b1d96c7b7421f496d229e119fd3d284e, 기존477개 source, Cargo 의존성/lockfile, native provider·EOS·FD·solver 허용오차·GL2 birth 처리와 transaction 규칙은 유지했다. 기존 Rayon batch도 바꾸지 않았고 cell-cache를 계속 선택한다. 이 batch를 borrowed 병렬 가속의 새 증거로 부르지 않는다.

## 4. 복사 감소와 실행 시간은 다른 관측량
fixed RadauN16의 실제 작업 계수는 다음과 같다.

| 계수 | CellCache | CellBorrowed |
|---|---:|---:|
| charged RHS attempts |2,992|2,992|
| occupied-cell preparations |14,720|14,720|
| node visits |1,914,880|1,914,880|
| cached prepared-state clones |2,704|0|
| cached prepared-node clones |1,730,560|0|

cache 생성 때 base clone, 좌표 decode, 변경 셀 재준비, O(C) 검사/diagnostics, O(M) 전체 rate 순회와 결과/보정 Vec6개의 할당은 남는다. 위 계수는 지정한 연산의 소스 수준 계수다. allocator 호출·전체 메모리·bandwidth·RSS를 측정한 수치가 아니다.

같은 binary, CPU0, profile-off, warmup 뒤 모드별 AB/BA5쌍으로 측정했다. 아래 ratio는 pair마다 cache 시간/borrowed 시간을 구한 뒤 중앙값을 취한 것이다. 두 별도 중앙 실행시간을 나눈 비율과는 다를 수 있다.

| 버전·clock | fixedN16 | birthN16 | disabledN16 |
|---|---:|---:|---:|
| v1 external-for, native |0.760293|1.030526|0.979692|
| 최종v2 for_each, native |0.932206|0.980651|0.879171|
| 최종v2 for_each, process |0.999237|0.876617|0.940714|

1미만은 borrowed가 느리다는 뜻이다. v2의 native paired ratio 범위는 fixed0.9232–0.9558, birth0.8816–1.1179, disabled0.6788–1.0398이다. 고정 모드에서는5쌍 모두 borrowed가 느렸고, 나머지 모드도 일관된 가속을 보이지 않았다. 각 sample과 IQR·범위를 그대로 보존했다. [v1 전체 통계](coder/evidence/C8_SUMMARY.json), [v2 전체 통계](coder/v2/evidence/C8_SUMMARY.json)

v2의 별도 단일 profile pair에서는 preparation0.08759→0.06775초, rates0.01607→0.02983초였다. 제거된 복사와 순회 방식 변화 사이의 비용 교환을 의심할 구체적 관측이지만, 한 profile pair로 원인을 확정하거나 profile-off paired 결과를 대체하지 않는다. 내부 Jacobian 시간은 다른 평가 시간과 겹치는 포함 시간이다. 여기에 준비·rate·provider 시간을 다시 더하지 않는다. 산술 연산 수가 같더라도 저장 배치와 컴파일된 순회 방식이 실측 시간을 바꿀 수 있다는 점까지가 이번 해석이다.

## 5. 재사용한 외부 코드와 다음 우선순위
Exa로 현재 Rust 공식 API 원문을 회수했다. SciSpace는 이전 회차에서 실제 검색하고 원문 확인한 자료를 재사용했으며 이번에 새 SciSpace 검색을 했다고 기록하지 않는다. 이전 CWI 최종 논문은 근사 Jacobian/solver 경계를 판단하는 보조 근거이고, 이번 exact borrowed 연산열 논증에 새 시간차수 권위를 부여하지 않는다. 회수 실패했던 LLNL 검색 결과는 결론 근거에서 제외했다.

VigilODE의 기존 solver/faer 및 독립 Rayon batch를 계속 사용한다. PR77의 제한된 hybrid 구조·local AD를 현재 native threshold/재구성의 전역 미분 정리로 옮기지 않는다. RUN19의 정확한 T-bit coefficient cache는 provider 비용이 실제 병목일 때 별도 작은 적용 후보다. 이번에는 도입하지 않았다. output/scratch workspace 재사용도6개 Vec 수명·reset과 failure 후 상태를 함께 설계해야 하는 후속 후보다.

다음 우선순위는 새 NCP 결과 유무를 확인한 뒤, 기존 cell-cache의 실제 NCP 실행을 완료하는 것이다. borrowed를 가속 기본값으로 승격하거나 측정 변형을 계속 늘리는 작업을 남겨두지 않는다. 이후 LU/provider 등 아직 분리되지 않은 비용 중 하나가 측정상 지배적일 때 그 한 경로만 별도 계약으로 다룬다.

## 6. 독립 판정·게시·보존
Astra root가 계약/수학/판정 기준을 소유했고 lower-tier coder가 구현·bounded 실행을 수행했다. 코드를 구현하지 않은 /root/opt20_intake_theory가 최종 diff와 실제 raw를 읽었다. C9의 문서상 v1/v2 표기 혼동1건은 문서만 고쳐 해결했다. 남은 blocking finding0, 독립 판정은 PASS_SCOPED_EXPERIMENTAL_IMPLEMENTATION이다. 실행 권한과 넓은 과학 주장 허용을 구분했다.

C1–C4는 commitd2d9ed9fa9f339448f2a6c3ba35d56c6d75280cb와 양쪽 백업 전체 GET/SHA로 완료됐다. 코드·핵심 receipt·C9·root 판정21파일은 sourcecommit5248822167e3fbe374f4333f7f2efdcdbfdaeeaf로 게시했으며 네 변경 소스와 C9 판정의 Git 원문 readback이 일치했다.

최종 새 원시 자료는 REI_LRS_BORROWED_C10_20261020B.tar.xz delta로 보존한다. 이는 독립 복원용 full base archive가 아니다. 기존 REI_LRS_OPTIMIZATION_C10_20261020.tar.gz,53,269,577byte,SHA623797d7a8b83b078f10ffaad780c7b2c223247e8b5593110c8d5f52286991b0 위에 새 repo_payload를 덮어 조합한다. 기존 base 전체 readback 근거를 재사용했다. 새 delta는 7,540,740bytes, SHA256492681e5ed7f1f53820b3bdcf24f397cfedbb6dac20a1d6dd917c7a9e2aa866e다. 로컬 압축본의 payload1,153개 manifest 검사를 통과했고, Drive와 Dropbox의 전체 GET에서 동일 크기·SHA256·HTTP200·exit0을 확인했다. 원격 회수본으로 native 시험을 새로 실행한 것은 아니다. Drive ID는1Dxj_adZQR4QEuxxatozwG10AMtvQw0z5, Dropbox ID는id:BSpOijBcT10AAAAAAD_SWQ다. 별도 ACK4,461bytes도 양쪽 전체 GET/SHA256 일치를 확인했다. 정확한 ID·시각·ACK 회수 정보는 [최종 전달](FINAL_DELIVERY.json)과 [원격 ACK](FINAL_PUBLICATION_ACK.json)에 있다. archive 내부 문서는 포장 전 상태를 보존하고 이후 원격 ACK는 sidecar/최종 Git metadata로 닫았다.

환경에 지정 SSH key가 없어 이번 source의 새 NCP 실행은 NOT_RUN이다. 과거d87ba9ca의 NCP19설정 완료를 새 source 실행으로 세지 않는다. 복사 가능한 [NCP 인계](CODEX_NCP_EXECUTE_KO.md)와 [다음 대화 prompt](NEXT_THREAD_PROMPT_KO.md)를 제공한다. 사용자에게 다운로드·수동 SSH/SCP를 요구하지 않는다.

## 7. 유지하는 과학적 범위
이번 결과로 source-on 일반2차, uniform stiff 정확도, 일반적 양수성, CaseB, fullEoR, signed Bianchi, positive-CMB/비영 boundary의 넓은 범위, continuous global certificate를 승격하지 않는다. 원시 photon energy와 boundary photon number의 완전한 독립 회계를 새로 확보했다고 말하지 않는다. production v3/rux·BASS 등의 DAG에 편입하지 않는다. 연구 산출물은 복사 제거의 정확한 구현·회귀 증거·부정적 성능 결과와 실행 가능한 후속 인계다.

