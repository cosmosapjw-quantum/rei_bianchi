# BASS_HE 다음 연구 루프 — PR19 이후 refinement와 정확 가중 합산

기준일: 2026-10-11 KST. 현재 계산 노드: `HE_E13C5_PR19_REFINEMENT_RECONCILIATION01`. Physmath research/coding GPT-6 Astra v4.0.0 하네스를 적용했다.

## 1. 결론과 이번에 새로 한 일

**기존 E13C5의 선택 12-path 결과를 보존하면서, OFF node 0·700을 N512로 refine하고 mode별 정확한 양의 가중 합으로 연결했다.** OFF selected-subset에서 최종 photon enclosure 전체 폭은 선행 결과보다 **9.405865배**, absorbed count 합은 **11.037777배**, absorbed energy 합은 **6.878873배**, heat 합은 **4.544328배** 좁아졌다. 이 수치는 고정된 captured 문제의 deterministic interval 폭이다. 새 물리 효과의 크기, 통계적 신뢰구간 또는 전체 spectrum 오차 허용값은 아니다.

두 OFF track의 incoming·anchor 계산은 `INDEPENDENT_REVIEW.json`에서 PASS_SCOPED, scientific blocker 0으로 판정됐다. PR19와의 의미 연결, exact reduction 및 새 NCP orchestration의 추가 판정은 `INDEPENDENT_LINEAGE_REVIEW.json`이 소유한다. 보고서나 성공 문자열 자체를 독립 판정의 대체물로 사용하지 않는다.

이번 실제 work는 네 번의 bounded enclosure 실행과 저장 결과에 대한 exact rational postprocessing이다. 새 coefficient evaluation은 총 **5,632회**, physics kernel elapsed 합은 **21.013605초**다. 실제 NCP에서 새로 실행한 것은 아니다. NCP handoff는 동일 N512 work unit 한 번과 그 fresh 결과의 exact reduction을 수행하도록 준비했다.

## 2. 선행 계보와 현재 기준

최초 intake는 PR17을 확인했지만, 별도 복구 폴더에 이미 출판된 PR18/PR19가 있었다. Publication 직전 발견하여 실제 head·source·결과·계약·리뷰를 복구하고 현재 순서를 갱신했다. 원래 PLAN과 raw evidence는 보존했다.

| 단계 | 실제 basis | 이미 완료된 범위 |
|---|---|---|
| E13C4 / PR17 | `8fc3fb14dd33da10efa86c97c4beb9b0d12eeaad` | Local remainder enclosure와 전달; scientific core `d1bb3ff33b7a448e3c08fc7b41467e2a7f94a146` |
| E13C5 OFF700 / PR18 | `48f648cd905cd8c232ae43abe97745ac6a96dec2` | 세 segment incoming·anchor pilot, source binding, scoped publication |
| E13C5 selected cover / PR19 | `e25039b3a53031ce37800cebefb51200aa5a63a2` | OFF/KF/GM × node 0/700/1620/2344, 12 paths·36 segments, N128/P60 |
| 이번 follow-up | 봉인된 신규 evidence 및 외부 delivery receipt | 공통 두 OFF 경로 N512 refinement, exact reconciliation, mode별 partial aggregate 교체 |

PR19의 36 segment 중 세 OFF700 segment는 pilot에서 재사용했고 33개는 신규 계산이었다. 선행 기록은 actual exit 0, wall **34.60초**, RSS **65,652 KiB**다. `publication_solver_reruns=0`은 출판 시 재실행하지 않았다는 뜻이며 선행 과학 실행이 없었다는 뜻이 아니다. 읽은 자료만으로 선행 host를 NCP라고 단정할 수 없다.

이번 두 경로는 **최초 E13C5 실행이 아니라 공통 부분의 추가 refinement**다. PR19의 NEXT_DAG에는 E13C6가 없고, full first2는 HOLD_RESOURCE_AUTHORIZATION이다. 이미 완료된 12-path cover를 다음 미완료 과제로 되돌리지 않았다. 원문은 `inputs/pr19_lineage/`, 검색 범위와 lineage 증거는 `evidence/lineage_intake/`, 초기 문서는 `evidence/pre_reconciliation/`에 있다.

## 3. 물리 문제와 incoming 보정

각 captured 구간은 \(x=\ln a\), \(u=x-x_a\in[0,h]\), \(E(u)=E_0e^{-u}\)를 사용한다. Photon 정규화는 상속된 photons per H per \(d\eta\)다. Energy·heat·redshift는 이 정규화에 eV를 곱한 단위이며 `eV norm.`으로 표시한다. Spectral coordinate \(\eta\)와 incoming uncertainty는 서로 다른 변수다.

\[
P'=q-\Lambda P,\qquad \Lambda=\sum_i\lambda_i,\qquad
\lambda_i=\frac{c\,n_i\,\sigma_i(E)}{H}.
\]

Gas stage의 affine interpolation, analytic FLRW \(H\), HI/HeI/HeII의 기존 cross-section fit, mask·source branch·energy anchor와 zero outflow를 유지했다. 실제 atomic RCT emission spectrum을 추가하지 않았다. 숫자는 captured binary64 값을 정확하게 lift하고, erg는 상속된 binary64 \(\epsilon=1.602176634\times10^{-12}\) erg/eV의 exact lift로 한 번만 변환한다.

정확 frozen 해 \(F\), frozen total opacity \(L\), \(\delta q=q-q_f\), \(\delta\Lambda=\Lambda-L\)에 대해

\[
e=P-F,\qquad e'+\Lambda e=\delta q-\delta\Lambda F.
\]

Incoming \(e_a\in[c_a-\varepsilon_a,c_a+\varepsilon_a]\)와

\[
B_r=\int_0^h\left(|\delta q|+|\delta\Lambda|F\right)\,du,\qquad
S=|c_a|+\varepsilon_a+B_r
\]

를 사용한다. \(\Lambda\ge0,F\ge0\)인 계약에서 \(S\)가 \(\|e\|_\infty\)를 제한한다. 각 observable의 firstvariation은 \(d_X+g_Xc_a\)이며 incoming uncertainty와 nonlinear remainder의 bound는

\[
|g_X|\varepsilon_a+S\int|T_X|
\]

이다. 정확 baseline 및 representation term은 별도로 포함한다. Photon endpoint gain은 \(e^{-Lh}\), total absorbed count gain은 \(1-e^{-Lh}\)다. Species energy·heat에는 각각 \(\lambda_{if}E_0J(L+1,h)\), \(\lambda_{if}[E_0J(L+1,h)-\chi_iJ(L,h)]\)를 쓴다. 누적 moment의 이미 쌓인 오차를 photon attenuation으로 감쇠하지 않는다.

선행 구현은 incoming interval \(I_a\)를 \(J_X+g_XI_a+[-ST_X,ST_X]\)로 직접 운반한다. 새 구현은 중심과 반경을 나누어 운반한다. 두 formulation은 같은 exact target을 다루지만 interval dependency와 rounding에 따라 endpoints가 달라질 수 있다. 선행 \(g_XI_a\)에 incoming uncertainty를 다시 더하지 않는다. 상세 bound 유도는 `THEORY.md`와 `evidence/lineage_theory/LINEAGE_REDUCTION_CONTRACT.md`에 있다.

## 4. 표현 기준과 energy seam을 맞춘 방법

선행 `continuous_minus_frozen`과 새 `true_minus_captured_interval`은 그대로 비교할 수 없다. 먼저

\[
(X-X_f)+(X_f-X_{\rm cap})=X-X_{\rm cap}
\]

로 기준을 맞췄다. Absolute photon은 prior Pend와 new true_absolute_interval, photon correction은 prior DP와 new true_minus_captured_interval을 비교했다. Prior cumulative_correction에는 frozen-minus-captured가 이미 포함되어 있다.

Energy stock에는 photon discrepancy만으로 복원되지 않는 표현 차이가 있다.

\[
E_hF_h-\frac{u_{\rm cap}}{\epsilon}
=E_h(F_h-n_{\rm cap})+\left(E_hn_{\rm cap}-\frac{u_{\rm cap}}{\epsilon}\right).
\]

Seam의 signed jump는

\[
\Delta E_j=E_{j+1,0}-E_{j,h},\qquad
J_j^{\rm anchor}=\Delta E_jP_{j,h},
\]

이고 전체 energy 장부는

\[
U_f-U_i+\sum_j(B_j+Z_j-Q_{E,j})-\sum_jJ_j^{\rm anchor}=0
\]

이다. DeltaE가 음수일 때도 signed interval product를 유지했다. `anchored=false`라는 flag만으로 작은 비영 seam을 버리지 않는다.

이번 네 실제 seam의 DeltaE는 두 양수와 두 음수다. Full ledger의 폭이 작은 anchor보다 클 수 있으므로 “장부 interval이 0을 포함한다”는 사실 하나로 anchor 누락을 판별하지 않는다. Signed product, native energy representation, incoming·누적 recurrence를 정확 Fraction으로 직접 확인하고, anchor를 빼면 실패하는 toy를 별도로 사용했다.

## 5. 공통 경로의 실제 수치

아래 \(C\)는 continuous-minus-captured 보정 후보, radius는 그 후보에 대한 절대 enclosure 반경이다. 짧은 표시값은 읽기용이며 정확 endpoint는 `evidence/N512_P60.json`이 소유한다.

| 경로 | 최종 photon C | Photon radius | 누적 heat C [eV norm.] | Heat radius [eV norm.] |
|---|---:|---:|---:|---:|
| OFF/0 | 3.214625619e-13 | 1.607172671e-18 | -3.265004695e-14 | 4.721279916e-19 |
| OFF/700 | 1.917944395e-13 | 8.110833422e-19 | -2.090850459e-12 | 9.709034948e-18 |

Node 0에서는 source가 꺼진 뒤에도 이전 photon stock을 운반한다. Node 700에서는 HeI mask가 꺼진 뒤 HI 채널과 incoming stock이 남는다. 첫 local segment의 correction만으로 전체 경로 correction을 대신하지 않았다.

PR19 ↔ 이번 N128 사이 302개, PR19 ↔ 이번 N512 사이 302개, 총 **604개 같은 quantity 비교에서 disjoint interval 0개**였다. Photon, 종별 moment, source, cumulative correction, erg/eV representation과 anchor가 포함된다. 이는 동일 target의 양립성 확인이다. 공통 coefficient·interval helper를 공유하므로 overlap 자체를 독립적인 물리 검증이라고 부르지 않는다.

| 경로별 진단 | 선행 폭 / 새 N512 폭 |
|---|---:|
| OFF0 final photon | 13.1901324 |
| OFF700 final photon | 14.6233621 |
| OFF0 cumulative total-heat native correction | 21.4009023 |
| OFF700 cumulative total-heat native correction | 14.7289928 |

기존 OFF700 reuse guard는 overlap만 확인했으므로 guard 자체를 충분조건으로 받아들이지 않았다. 원 pilot의 세 saved incoming endpoint와 cover incoming endpoint가 정확히 같고, pilot interval이 exact rational previous-Pend−captured-f0를 포함하는지 직접 확인했다. 재사용 Pend/J/g/remainder/frozen/captured/corrected payload도 일치했다. 이 saved reuse의 연결은 확인됐지만 overlap-only guard를 일반적인 재사용 인증으로 승격하지 않았다.

## 6. 선택 부분집합의 정확한 가중 합

Mode \(m\)마다 \(S_m=\{0,700,1620,2344\}\) 네 node를 합한다. OFF/KF/GM은 대안 gas history이므로 서로 더하지 않는다. Captured spectral weight는 exact-lift한 양수다.

\[
I^{\rm refined}_{{\rm OFF},X}
=\sum_{p\in\{1620,2344\}}w_p I^{128}_{p,X}
+\sum_{p\in\{0,700\}}w_p I^{512}_{p,X}.
\]

기존 aggregate에서 두 interval을 빼는 방식은 dependency를 다시 넓힐 수 있다. 유지되는 개별 term 열 개와 교체하는 term 두 개에서 정확 Fraction endpoint 합을 다시 만들었다. KF/GM의 published aggregate를 보존했고, OFF의 14개 quantity는 모두 기존 OFF interval 안에 포함됐다.

| OFF selected-subset quantity | 기존 전체 폭 | 새 전체 폭 | 감소 배수 | 단위 |
|---|---:|---:|---:|---|
| Final photon | 9.938955540e-23 | 1.056676343e-23 | 9.405865 | number norm. |
| Absorbed count | 2.119338316e-22 | 1.920077123e-23 | 11.037777 | number norm. |
| Absorbed energy | 3.540828245e-21 | 5.147396132e-22 | 6.878873 | eV norm. |
| Heat | 5.312111378e-22 | 1.168954212e-22 | 4.544328 | eV norm. |
| True anchor | 2.505190356e-37 | 2.067006596e-38 | 12.119895 | eV norm. |

여기서 total A/B/H는 **종별 interval의 합**이다. 앞 표의 경로별 dedicated total-heat correction certificate와 endpoint가 같을 필요는 없다. 두 표의 관측량·baseline·weight 및 radius/width를 구별했다. 그림은 각 quantity의 기존 폭을 1로 정규화한 진단이다.

![OFF selected-subset interval width comparison](figures/PR19_REFINEMENT_WIDTHS.png)

Captured segment-to-node reduction은 입력의 표현 차이로 따로 보존했다. 새 두 경로의 각 step에 대해 continuous-minus-segment correction과 원래 segment-minus-node term을 합한 native-node bridge **네 개**도 계산했다. 이 bridge가 전체 native AGGREGATE.csv의 error를 인증하는 것은 아니다. Full spectrum이나 실제 native aggregate floating-point rounding에 대한 새 certificate는 없다.

## 7. 실제 실행과 검증

| 작업 | 실제 범위 | 결과 |
|---|---|---|
| 두 경로 enclosure | N32/P60, N128/P60, N512/P60, N32/P80; serial 네 번 | 모두 exit 0; coefficient 5632; kernel 합 21.013605초 |
| 새 N512 계산 | 네 local 신규 + 동일 두 local certificate 재사용 | Kernel 14.929506초; RSS 15,556 KiB |
| 별도 theory toys | Fraction/formal series 92개 | PASS; candidate import·새 coefficient 0 |
| 별도 recurrence control | exact toys 76 + saved checks 3867 | PASS; 3867 중 interval-order 1626을 구별 |
| 두-track decision reviewer | Saved exact Fraction 감사 138개 | PASS; scientific blockers 0 |
| Lineage 최종 postprocessing | N128 진단 포함 1180 checks / 604 comparisons | Exit 0; 0.266535초; 새 coefficient 0 |
| NCP 형식 reducer 확인 | N128 진단 생략 774 checks / 302 comparisons | Exit 0; 0.215819초; projection bytes 동일 |
| Lineage decision reviewer | Carry·mode 합·유지 term·native bridge 등 199 checks | PASS; 새 coefficient/solver 0; 별도 최종 review 파일 참조 |

Lineage 최초 실행 뒤 interface metadata를 보완하면서 saved-output postprocessing만 다시 수행했다. 원 source/v1 결과를 유지했고 physics solver는 다시 돌리지 않았다. 기여 보고서 수식의 표시 오류도 원 문서를 보존한 뒤 표시만 고쳤다. 원 theory/recurrence control의 최초 실패와 수정은 respective evidence에 남아 있다.

새 NCP wrapper의 합성 경계검사에서는 최초 11종 중 10종이 예상대로 동작했고, 실행 중 잠금 목록 자체 변경을 놓치는 한 문제를 찾았다. 실제 lock-file SHA 전후 비교를 추가한 뒤 해당 실패와 인접 success/verify-only 세 case만 확인해 **3/3**을 통과했다. 최초 실패를 보존했으며 11종 전체를 수정 후 다시 돌렸다고 주장하지 않는다. 실제 package의 수정 후 verify-only도 exit 0, 0.215406초였고 새 물리 실행은 0이다.

합성 fixture의 PASS 문자열은 실행 제어 시험용이다. 실제 NCP 실행이나 과학 정확도 검증으로 집계하지 않는다. 별도 process-create transport failure도 runtime failure로 보존하고, 대상 output이 없음을 확인한 뒤 verify-only만 재시도했다.

## 8. NCP 전달과 실행 계약

NCP_READY ZIP 한 개 안에 실행문, scientific ZIP, receipt, 필요한 입력·선행 결과·code·review·manifest를 모두 넣는다. 별도 입력 파일의 추가 전달은 필요하지 않다. Publication 또는 백업 ACK는 실제 NCP 실행이나 recipient ACK가 아니다.

`code/ncp_continue.py --execute`는 19개 잠긴 파일과 lock 자체의 identity, CPython 3.12.x·serial host 조건을 확인한다. 한 번의 N512/P60 계산을 수행하고 fresh source identity와 전체 deterministic numerical projection을 비교한다. 이어 그 fresh 결과 SHA에 결합된 exact reduction을 한 번 실행하고 raw evidence와 RETURN_MANIFEST를 만든다.

Physics numerical SHA는 `f4d0f8c7e37e5c8a013ab133af748173f3ef1a8247f413f4798fdb3518c04a86`이다. Reduction projection 파일은 **419,815 bytes**, SHA `f0681b18032e4de92db2a4d4c867d00895cf761bbdb5a57c571fba6e0e01bb69`다. 후자의 canonical-object hash는 newline 제외 기준이므로 file hash와 구별한다.

실행 예산은 science **180초·1 GiB**, exact reduction **60초·1 GiB**, 각각 한 번, process/thread 1, MPI 0이다. 바깥 physics wrapper의 205초에는 host intake와 종료 기록이 포함된다. Default verify-only는 NOT_RUN/NOT_EVALUATED다. 실제 성공 조건은 `PASS_SCOPED_HOST_PARITY_AND_REDUCTION`과 정확히 1+1회의 실행·fresh identity·projection 일치다. 상세 명령과 반환 절차는 `NCP_LOCAL_CODEX_HANDOFF_KO.md`에 있다.

## 9. 다음 연구 질문과 한계

선택 경로의 interval을 좁히는 것과 전체 spectral node contribution을 제한하는 것은 다른 작업이다.

\[
M^{\rm full}_{m,X}=M^{\rm selected}_{m,X}
+\sum_{p\notin S_m}w_{m,p}X_{m,p}.
\]

이번에는 두 번째 항의 uniform upper/lower bound를 계산하지 않았다. Correction은 signed일 수 있으므로 네 selected node의 correction이 작거나 같은 부호라는 사실로 complement를 제한할 수 없다.

다음 node는 **E13C5_SELECTED_SUBSET_BUDGET_AND_MISSING_NODE_COMPLEMENT_CONTRACT**다. 저장 결과에서 남은 selected-subset 폭을 분해하고, 미포함 node의 weight·mask/source/event branch 분할을 조사한다. Complement 상계 또는 빠진 가정을 명시한 뒤 measured resource 계약과 독립 판정으로 다음 계산을 고른다. 이 준비 단계의 기본 새 coefficient/solver 실행은 0이며, 자동 E13C6 지정이나 full first2 실행은 없다.

| 상태 | 이번 결과 이후 |
|---|---|
| 두 OFF fixed-path enclosure | Scoped 독립 판정 |
| 기존 selected 12-path cover | 선행 scoped 판정 보존 |
| 두 항 교체에 따른 mode별 aggregate | 추가 독립 판정의 범위 |
| Full first2 / full spectral uniform certificate | HOLD_RESOURCE_AUTHORIZATION / 미인증 |
| 새 gas evolution / native full aggregate | 미실행 |
| Actual atomic photon/heat/recoil | null |
| Physical / production | HOLD |
| HE-F2/F09 / receiver adoption | OPEN / SEPARATE |
| Legacy Gamma alias 3.543295 | FAIL 유지 |

## 10. 근거 파일과 재현 위치

새 수치는 실제 saved data에서 가져왔다. Hash는 byte identity의 근거이며 과학 타당성 또는 실행 권한의 대체물이 아니다.

- `evidence/N512_P60.json`, `PHYSICAL_RESULT.json`: two-track endpoint·중심·반경·실행 요약.
- `inputs/pr19_lineage/first2/RESULTS.json`: 선행 12-path 결과 SHA `418dcac9280947abc227c69f9178c0163bbdb00fa34bff1f9e34ab9eea35ece4`.
- `code/lineage_reduction.py`: exact semantic/reduction source SHA `dd8796ae232d3d72384df14263658d1e48e87a8fad6982f64a6ab811ce2eb985`.
- `evidence/lineage_control/output_v2/RESULTS.json`: 1180 checks·604 comparisons·mode별 term/aggregate·native-node bridge 전체.
- `evidence/lineage_control/PROTOCOL_CHECK.json`: NCP 형식 projection byte identity.
- `evidence/lineage_theory/LINEAGE_REDUCTION_CONTRACT.md`: incoming·양의 가중 교체 유도와 조건.
- `INDEPENDENT_REVIEW.json`, `INDEPENDENT_LINEAGE_REVIEW.json`: 별도 독립 판정과 직접 읽은 identities.
- `evidence/ncp_continuation_boundary/`: 최초 wrapper failure와 focused repair; 합성 fixture임을 명시.
- `FILE_MANIFEST.json`: 전체 package payload identity. 실제 publication과 백업 ACK는 외부 delivery receipt 및 backup ACK.

원격 원문: [PR18](https://github.com/cosmosapjw-quantum/BASS_HE/pull/18), [PR19](https://github.com/cosmosapjw-quantum/BASS_HE/pull/19), [PR19 고정 결과](https://github.com/cosmosapjw-quantum/BASS_HE/blob/e25039b3a53031ce37800cebefb51200aa5a63a2/research/e13c5_first2_branch_cover_20261011/RESULTS.json). Arithmetic runtime 조건은 [Python 3.12 Decimal 문서](https://docs.python.org/3.12/library/decimal.html)와 상속 directed_interval source를 구별해 사용한다. 이번 실제 interpreter는 CPython 3.12.14, libmpdec 4.0.0이다.
