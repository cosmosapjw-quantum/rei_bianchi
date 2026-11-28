# 독립 R6 최종 판정 — HERE_RUX03_MOVING_GAS_SOURCE_05

**판정: PROMOTE_SCOPED_THEORY — 고정된 가정 아래 M01–M07의 이론 결과를 채택한다.**

검토자: /root/dropbox_checkpoint. 판정 시각: 2026-10-12 23:21:21 UTC.

중대한 수학·단위·부호·실행 근거 오류와 열린 material finding을 발견하지 않았다. 채택 범위는 하나의 공통 gas velocity, 고정 local Eulerian tetrad와 lab volume, 기존 warm Case A provider를 갖는 homogeneous source step이다. 실제 moving solver, 정량적인 full-rate 시간 간격 인증 또는 임의의 큰 시간 간격에 대한 전역 coupled-stage 해의 존재·유일성은 이번 채택에 포함되지 않는다.

## 1. 검토 대상과 독립성

최종 [CANDIDATE_MANIFEST.json](../dossier/CANDIDATE_MANIFEST.json)의 SHA256은 **ba7ef487639f4bd2686353293c4afbe91d421fec9a9cf8eef6d242aa410c6680**이다. 고정된 **45개 파일, 340,648 bytes** 전부에 대해 실제 bytes, SHA256, Git blob SHA1을 대조했고 모두 일치했다. 개별 identity 전체는 [DECISION.json](DECISION.json)의 candidate_binding에 수록한다.

초기 두 유도와 원 실행 입력·출력의 독립 검토는 [INTERIM_R6_v1.json](INTERIM_R6_v1.json)에 보존했다. 최종 검토는 그 결과를 재사용하고 추가된 REPORT, CODING_CONTRACT, CLAIMS, HANDOFF, NEXT_DAG, LOOP_RECORD, source map 및 실행·재현 문서와 교정 범위를 읽었다. 판정은 작성자의 완료 표기나 PASS 개수만으로 결정하지 않았다.

검토자는 일차 문헌 조사와 검토 기록만 작성했다. 후보 유도·코드·수용기준·기호검산 입력을 작성하지 않았으며 이 unit에서 과학 evaluator, native build, RHS, ODE 또는 parameter scan을 실행하지 않았다. 마지막 파일 hash와 JSON decoding은 실행 근거의 직렬화·identity 검증이다. 고정된 45개 후보 파일은 수정하지 않았다.

## 2. M01–M07별 판정

| Claim | 채택 범위와 검토 근거 | 남은 의무 |
|---|---|---|
| **M01** | \(\delta=\gamma(1-\beta\cdot e)>0\), \(E'=\delta E\), \(N'=\delta N\), \(\lambda=c(D/\gamma)y\,\sigma(E')\delta\)의 정의·차원이 맞는다. 동일한 scalar four-volume 사건률 \(R'=\lambda N\)에 lab 간격 \(h\)를 곱해 종의 사건 수를 얻는다. per-H gas clock의 \(h/\gamma\) 표현과 일치하며 추가 Lorentz 인자가 필요하지 않다. | 실제 provider에 proper density 및 lab/reference photon 변환을 구현하고, atomic support는 Doppler 변환 후 \(E'\)에서 검사한다. |
| **M02** | 같은 endpoint에서 얻는 \(N^+=(N^-+hS)/(1+h\Lambda)\)와 종별 사건 수가 gas·photon·escape의 유한 에너지 및 세 운동량 수지를 보존한다. 비음수 입력과 admissible endpoint가 주어진 경우 photon map의 비음수성은 모든 \(h\ge0\)에 성립한다. 이 조건부 명제와 coupled endpoint 존재 명제가 구분되어 있다. | 단일 사건 bundle 및 endpoint 소비를 구현한다. RR/DR escape energy moment로부터 새 방출 photon 수·spectrum을 만들지 않는다. |
| **M03** | 고정 composition에서 \(D>0,r>0\)일 때 양의 thermal primitive는 \(\mathcal E>\sqrt{(Dr)^2+|\mathcal M|^2}\)와 동치이며 유일하다. 스칼라 enthalpy map의 단조성·치역, 양의 항으로 쓴 gap, bracket, 미분 및 warm-domain 검사가 일치한다. \(M=0\)에서도 부당한 나눗셈이 없다. 일반 cone 정리는 기존 gamma-law 정리의 특수화로 적절히 귀속했다. | cold equality는 수학적 경계이며 warm model 밖이다. 구현은 unsquared physical root, bracket, warm admission과 작은 energy gap의 정밀도 예산을 보존해야 한다. 이미 반올림으로 잃은 gap을 공식 재배열이 회복한다고 보장하지 않는다. |
| **M04** | endpoint stress projection과 공유 binding/escape ledger에서 도출한 유한 \(K_\gamma\) 열수지가 정확하다. 아래 식의 부호·단위·endpoint placement와 연속극한을 확인했다. Eulerian homogeneous pressure가 gas rest frame에서 spatial gradient를 가질 수 있다는 설명도 맞는다. | full conserved energy/momentum으로 primitive를 정하고 thermal 식은 진단으로 사용한다. 여덟 번째 독립 방정식으로 더하지 않는다. 유한 pressure·relative-velocity correction과 작은 차이의 정밀도를 유지한다. |
| **M05** | strict smooth physical interior에서 full primitive Jacobian은 가역이고, \(h=0\)에서 7변수 residual의 state derivative는 항등이다. 따라서 주장된 국소 \(C^1\) branch가 성립한다. 주어진 compact physical ball에서 \(hM_0\le r_{\rm ball}\), \(hL_0<1\)은 구성적 contraction 충분조건이다. | 실제 full-rate box의 \(M_0,L_0\)나 동등한 residual/Jacobian bound는 아직 계산·인증하지 않았다. cutoff·warm·simplex·primitive 경계를 추적하는 정량 continuation certificate가 다음 THEORY 의무다. |
| **M06** | 23 eV HI-only recoil family는 binding, electron count, proper-density 변화와 양의 endpoint photon inventory를 일관되게 포함한다. 엄격한 초기 warm 상태 부근에 양의 fluence 구간이 존재한다. 반대 방향 동일 pair의 zero recoil·온도 평균식도 맞다. full-rate rest-paired branch의 scalar 환원은 대칭과 국소 유일성에서 따른다. | 명시적 fixture는 channel-isolated reference다. full FT03 trajectory로 해석하지 않는다. endpoint마다 구성한 입력은 고정된 입력의 임의 timestep 해 존재를 증명하지 않는다. thermal cone만으로 warm/spectral admission이 완료되지 않는다. |
| **M07** | 현재 source와 새 이론 사이 per-H/proper/fixed-lab-volume, eV/erg, Doppler 및 angular 변환 계약을 채택한다. axial velocity에서는 \(\mu\) ring의 Doppler opacity가 azimuth와 무관하다. transverse velocity에서는 실제 azimuth를 분해하거나 pointwise 적분해야 한다. ring 평균 방향을 unit null ray로 취급하지 않는 제한이 명확하다. | receiver에는 아직 moving \(\mathcal E,\mathcal M,\beta\) primitive solver가 없다. 기존 primary-provider 및 covariant-moment 선행 coding 의무와 angular quadrature 정확도 검증을 유지한다. |

M04에서 \(\epsilon=\epsilon_{\rm eV}\), \(\Gamma=5/3\)일 때 채택한 항은

\[
K_\gamma=D\left[
(r_-+\Gamma\epsilon w_-)(\gamma_{\rm rel}-1)
-(\Gamma-1)\epsilon w_-\left(\frac{\gamma_+}{\gamma_-}-1\right)
\right],
\qquad
\Delta w=\frac{h}{\gamma_+}Q_{\rm th}^{(H)}
+\frac{K_\gamma}{D\epsilon}.
\]

매끄러운 극한에서 \(\gamma_{\rm rel}-1=O(h^2)\)이고 첫째 차수 pressure work가 \(-\tfrac23 w\,\Delta\ln\gamma\)를 준다. 따라서 \(\dot w=Q_{\rm th}^{(H)}-\tfrac23\Theta w\)와 일치한다. 유한 backward Euler map은 지정된 time foliation의 이산화이며, 다른 관측자 foliation에서 동일한 유한 map이라는 보장은 하지 않는다. 근거는 [root 유도](../derivations/MOVING_SOURCE_AND_THERMAL_BALANCE.md), [primitive 유도](../derivations/PRIMITIVE_RECOVERY_AND_EXAMPLES.md), [CLAIMS](../dossier/CLAIMS.json)다.

## 3. 실제 실행과 검증 수의 해석

| 실제 batch | 최종 관측 | 독립 검토 |
|---|---:|---|
| xTensor/xPerm | 25/25 True, tensor residual 모두 0 | 최종 raw decoding과 normalized object가 동일하다. v3 wrapper의 embedded program이 canonical tensor program과 같다. 실제 xTensor 1.3.0 / xPerm 1.2.4, Wolfram 15.0.1을 사용했고 xPerm은 pure Wolfram backend다. |
| Primitive inverse / fixture | 18/18 True | 17 algebra·derivative 그룹과 1 exact-rational fixture 그룹이다. raw의 모든 필드는 유지되었고 normalized record는 execution receipt만 추가했다. |
| Finite source / Jacobian | 12/12 최종 명명 항목 | 첫 actual run의 11개 성공과 별도 positivity 1개 성공을 합친 명시적 per-assertion aggregation이다. 하나의 all-pass kernel run으로 보고하지 않는다. |

최종 batch의 raw 명명 항목은 **25+18+12=55**다. registry가 선언한 공통 primitive Jacobian target 한 개를 제외하면 **54개 bookkeeping target**이다. 이 수는 서로 독립적인 정리나 물리 시나리오의 수가 아니다. scalar와 tensor 표현 사이에 의도된 물리 항등식 교차검사가 있다. 과학적 주장은 **M01–M07의 7개 family**로 심사했다. 이전 THEORY04의 45개, THEORY03의 47개 그룹은 새 실행 수에 포함하지 않는다. [실행 기록](../evidence/EXECUTION_RECORD.md)

실제 evaluator 호출은 여섯 번이다. xAct v1·v2는 completed PASS JSON 없이 Hold[Throw[Null]]을 반환했다. diagnostic 위치와 helper의 고정 dummy index를 대조하면 Cp[b]에서 free/dummy index가 충돌한다는 진단이 뒷받침된다. v3는 동등한 expanded current로 이를 고치고 stress-current 동치 검사를 추가했다. raw 자체가 충돌 원인을 문장으로 설명하는 것은 아니다. 물리 규칙·정의역·기준을 완화하지 않았고 실패 원자료가 보존되어 있다.

첫 scalar run의 primitive_jacobian_positive는 conditional radical inequality가 남아 TrueQ가 False로 기록한 것이다. 음수 determinant 값이나 반례가 관측된 것이 아니다. 보완 실행은 \(\alpha=2+a\), \(a\ge0\)에서 원 determinant를 전개하여 22개의 비음수 계수와 엄격히 양인 \(a_r^3\gamma^5\) 항을 확인했다. 원래 양의 domain에서 해당 한 항목을 닫으며 이미 성공한 11개는 재실행하지 않았다.

최종 metadata 검증에서 두 scalar call-input의 code bytes가 보존된 executed WL과 정확히 같음을 확인했다. canonical derivation WL은 executed WL에 마지막 LF 한 개만 더한다. 두 raw object는 각각의 normalized result와 정확히 일치하며 최종 aggregate는 지정한 한 target과 상태·집계 기록 외에 원 실행 결과를 변경하지 않는다. local JavaScript 준비 오류는 evaluator 호출 전의 파일 준비 오류로 별도 공개되어 있다.

CAS 결과는 지정한 항등식·fixture를 검산한다. 전역 primitive 단조성, 국소 해 정리와 contraction 충분조건은 본문 증명을 읽고 채택했으며 PASS 개수로 추론하지 않았다.

## 4. 발견과 최소 교정의 폐쇄

| Finding | 원래 관측 | 최종 상태 |
|---|---|---|
| **R6-E01 — attribution** | primitive §9가 기존 gamma-law global cone theorem을 새로운 일반 정리로 읽히게 할 수 있었다. | Wu–Tang 정리의 specialized rederivation으로 교정했고 프로젝트 연결 성과와 분리했다. 식·검산 기준은 불변이다. |
| **R6-E02 — bibliography** | Sądowski 원전의 표시 제목이 실제 제목과 달랐다. | 원래 “Semi-implicit scheme for treating radiation under M1 closure in general relativistic conservative fluid dynamics codes” 제목으로 수정했다. URL·인용 식 범위는 유지했다. |
| **R6-E03 — rendering** | 실행 기록의 eV 변환상수 아래첨자가 의도하지 않은 newline으로 갈라졌다. | 최종 \(\epsilon_{\rm eV}\) 표기를 직접 확인했다. 과학 값·결과는 불변이다. |

최종 primitive 문서의 추가 세 immutable parent link 수정도 전달용 변경이다. 초기 검토와 historical author snapshot의 이전 hash는 당시 identity로 보존되며, 최종 identity는 현재 manifest가 우선한다. 과학 입력·출력 재실행이 필요한 교정은 없었다.

## 5. 문헌·source authority·인계

문헌 증거는 [LITERATURE_MAP](LITERATURE_MAP.md), [SOURCE_EVIDENCE](SOURCE_EVIDENCE.json), [SEARCH_EVIDENCE](SEARCH_EVIDENCE.json)에 보존했다. 세 Exa query의 15 requested slots와 한 SciSpace query의 10 entries는 전체 논문 읽기 수가 아니다. 필요한 네 원전의 지정된 식·section을 읽었고 중복 검색 결과와 metadata 교정을 기록했다.

- [Younsi, Wu & Fuerst (2012)](https://arxiv.org/pdf/1207.4234), 인쇄 pp. 2–3, 식 (9)–(17): invariant opacity와 frequency-shift 관계를 확인했다. 논문의 frequency-shift 표기와 gas Lorentz factor를 구분했다.
- [Sądowski et al. (2013)](https://arxiv.org/pdf/1212.5050), §§3.3–3.5, 식 (50)–(56): local implicit conservative source 구조의 선행 근거다. 그 논문 자체도 실패 가능성을 논의하며 이번 전역 nonlinear solvability를 보장하지 않는다.
- [Wu & Tang (2015)](https://arxiv.org/pdf/1504.07707), 인쇄 pp. 5–7, Lemma 2.1 및 식 (2.3)–(2.5): gamma-law cone·physical primitive 유일성의 선행 근거다.
- [Cai, Qiu & Wu](https://arxiv.org/pdf/2305.14805), unsquared pressure 식 및 인쇄 pp. 8–9의 Theorem 2.1–2.2: squared quartic의 추가 양의 root와 실제 physical root를 구분하는 근거다. 기존 Newton 수렴 연구를 이번 구현 성과로 옮기지 않았다.

Farris et al.의 일반 four-force와 Rosdahl–Teyssier의 저속 에너지·운동량 대응은 이전에 확인한 범위로 재사용했다. 이전 A7/A8 convention의 미해결 모호성을 이번 exact covariant 결론의 근거로 사용하지 않았다. parent의 네 원전 직접 열람은 [ROOT_PRIMARY_READS](../evidence/ROOT_PRIMARY_READS.json)에 별도로 기록되어 있다.

현 source authority는 bounded survey와 retained identity에 따른 BASS_HE PR32 head **ca85cfc7353da190613f7fb37a6e0ffed9b51913**, receiver PR114 head **a5c958c414dea41216b445c05f58df837f05cacb**다. 선택 production 경로는 SourceBoundConditional::evaluate_detailed → detailed_rhs → CaseAEventBundle::into_ledger → axisym_coupled_derivative이며 공개 provider는 고정 FT03다. 이 검토가 이후 미관측 외부 변경의 부재를 보장하지 않는다. [Source map](../source_map/SOURCE_MAP.md)

다음 THEORY는 **HERE_RUX03_MOVING_GAS_CONTINUATION_CERTIFICATE_06**이다. 실제 full-rate physical box, scaled norm, 정량 source/Jacobian bound 및 양의 certified step을 구성하는 의무가 남는다. Coding 쪽은 **HERE_RUX03_PRIMARY_PROVIDER_03**, **HERE_RUX03_COVARIANT_MOMENTS_04**의 선행 의무를 유지한 뒤 **HERE_RUX03_MOVING_GAS_STAGE_05**로 이어진다. 원 RUX02·global RUX03 → RUX04 → RUX05 순서와 별도 D2.3 scope는 변경하지 않는다. 이번 채택은 strong no-go나 global RUX03 종료 선언이 아니다. [NEXT_DAG](../dossier/NEXT_DAG.json), [HANDOFF](../dossier/HANDOFF_KO.md)

작성 시점 snapshot의 R6/R10 pending은 이후 독립 결정·행정 closeout이 완료 상태를 기록하도록 남긴 구분이며 material 인계 불일치가 아니다. parent는 이 결정과 CLOSEOUT, final science manifest, publication·backup 기록을 추가할 수 있다. 고정 과학 파일을 바꾸는 경우에는 변경 범위를 별도로 식별해야 한다.

