# HE-EXP-INTAKE-01 — 전종 공급자 입력과 조건부 교환·열폐쇄

## 이번 결과

고정 인계 c456b05e0f1c53faa3ae36720826f43e57c06a91에서 이어 받아, WU/REC의 실제 species·scalar 공급자 행과 Mutation++의 실제 충돌 자료를 HE 소비자 입력으로 연결했다. 새 source inventory와 유한질량 교환·입자수·열용량·에너지 소유권 어댑터를 구현했다. 전체 미분 충돌 공급자의 물리적 완성은 입력 의존성으로 남아 있다.

| 결과 | 확보한 범위 | 근거 상태 |
|---|---|---|
| 종별 소비자 registry | 원자 charge state 20, neutron 1, 전자 pool 2, synthetic extension 9 | implementation-verified; 원 fixture qualification 보존 |
| 원자 scalar 공급자 | PI 6, RR 6, CI 6의 실제 계수 행 | source-intaken; isotope equality 근사 명시 |
| 수송 입력 | explicit pair 27, Q expression 243 | source-intaken; thermal collision integrals |
| 선택된 H–He 입력 | Q11,Q12,Q13,Q14,Q15,Q22,Q23,Q24,Q33; 기존 Q11/Q22 원본 일치 | source-intaken / scoped reuse |
| 유한질량 교환 | full-angle elastic moment 입력에서 운동량·에너지·tensor 증가량 | derived; implementation-verified under stated inputs |
| 열·count·energy closure | thermal/nonthermal pool 분리, 일반 caloric chain rule, 단일 energy owner, drift stress | derived; implementation-verified |
| 전체 physical provider | 새 승인 0 | source-input-pending |
| 전체 물리 완료율 / L4 | null / false | 유지 |

이 문서의 23 baseline slots는 20개 원자 전하 상태에 neutron 1개와 두 전자 pool을 더한 것이다. WU의 합성 확장 9개는 실제 isotope/state/molecular 공급자와 구분한다. 미래 종 목록은 확장 가능하며 일곱 동위원소가 상한을 정하지 않는다.

## 실제 입력과 재사용

소스 경로와 blob/SHA256은 [SOURCE_PROVENANCE](sources/SOURCE_PROVENANCE.json), [species registry](species/SPECIES_PROVIDER_REGISTRY.json), [explicit transport inventory](species/EXPLICIT_TRANSPORT_SOURCE_INVENTORY.json)에 있다. 실제 XML은 Mutation++ commit 58678c0e038eb2f078fed3b45640741fdaf167dc의 data/transport/collisions.xml이다. 155227 bytes, Git blob d86bf74e05e6bcac9db67cfc03055621ebed2f8c, SHA256 25e0ac6affa33361e9652d3fd3f43760f40f1a500c0a4993b1ace82c5ce501c2를 보존했다.

명시적 pair는 e–H/H2/He, H–H/H+/H−/H2/H2+/H3+/He/He+/He++, H+–H2/He, H−–H2/He, H2–H2/H2+/H3+/He/He+/He++, H2+–He, H3+–He, He–He/He+/He++다. 각 pair의 9개 Q expression을 원본의 nested 구조와 decimal coefficient로 보존한다. 자동 default, endpoint clipping, fit 평가 또는 isotope substitution은 실행하지 않는다.

\(\overline Q^{(\ell,s)}(T)\), 고정 상대 에너지의 \(\sigma_\ell(E)\), \(d\sigma/d\Omega\), ionization의 same-event joint law는 서로 다른 객체다. 소비자 요청의 quantity가 source에 없으면 명시적으로 거절한다. H source label을 D/T로 재사용하려면 keyed assumption을 요구하며 결과는 CONDITIONAL_ALIAS_ONLY다. 실제 질량·상태·오차와 physical admission은 별도다.

HD는 REC owner의 고정 계약으로 연결했다. J0–8, 미확정 vibrational label, p/o-H2 collider 2/3, exact \(T=50,100,200\) K를 유지한다. HE는 REC의 level/collider parser를 중복 작성하지 않았다. source-selected 분자·음이온·isomer와 WU synthetic 확장을 서로 대체하지 않는다.

HE33/36/38의 원문과 source identity는 [exchange provenance](exchange/PROVENANCE.json)에 있다. HE34의 기존 H–He Q11/Q22 자료를 재사용했고, HE101의 과학 suite·plot·export 및 WU의 기존249-check를 재실행하지 않았다.

## 유한질량과 각도 모멘트

비상대론적 국소 관성계에서 \(m_a,m_b>0\), \(M=m_a+m_b\), \(\mu=m_am_b/M\), \(\mathbf g=\mathbf v_a-\mathbf v_b\), \(\mathbf V=(m_a\mathbf v_a+m_b\mathbf v_b)/M\)를 사용한다. 관련 속도는 \(c\)에 비해 작아야 하며 source의 COM 상대 에너지 범위를 만족해야 한다. SI의 \(k_B\)를 유지한다. 구조 유도는 [exchange/THEORY_KO.md](exchange/THEORY_KO.md)에 있다.

완전한 COM 각도 지지와 상대속도축에 대한 회전 대칭을 갖는 elastic 사건에 대해
\[
\sigma_0=\int d\sigma,\qquad
\sigma_\ell=\int[1-P_\ell(\cos\chi)]d\sigma
\]
를 정의한다. 각도 적분된 event 증가량은
\[
\int\Delta\mathbf p_a\,d\sigma=-\mu\sigma_1\mathbf g,\qquad
\int\Delta E_a\,d\sigma=-\mu\sigma_1\mathbf V\cdot\mathbf g,
\]
이며 \(b\)종의 증분은 반대 부호다. 두 종 second-moment의 합은
\[
\int\Delta(m_a v_{a,i}v_{a,j}+m_bv_{b,i}v_{b,j})\,d\sigma
=-\mu\sigma_2 g_{\langle i}g_{j\rangle}.
\]
따라서 에너지 trace는 보존되고 anisotropic stress의 변화는 \(\sigma_2\)를 사용한다. event frequency 또는 \(\sigma_0\)를 그 이완률로 대체하지 않는다.

이 값은 cross-section-weighted event increment다. 분포 공급자는 같은 법칙에 대해 \(f_af_b|\mathbf g|\)를 적분해야 체적당 교환률을 얻는다. source가 finite angular window이거나 thermal integral만 제공하면 full-angle interface로 들어오지 못한다. Ionization recoil의 cross-moment는 이 elastic 식으로 채우지 않는다.

## 실제 H–He 수송 입력과 열화식의 연결

서로 구별되는 고전 Maxwell 종이며 bulk drift가 없고 elastic source가 유지된다고 하자. 상대 온도와 평균 상대속도는
\[
T_*=\frac{m_bT_a+m_aT_b}{M},\qquad
\overline g=\sqrt{\frac{8k_BT_*}{\pi\mu}}.
\]
Bruno source의 정규화는
\[
\overline Q_{11}(T_*)=\frac12\int_0^\infty e^{-x}x^2\sigma_1(x)\,dx
\]
다. Gaussian 조건부 평균
\[
\mathbb E[\mathbf V\mid\mathbf g]
=\frac{\mu(T_a-T_b)}{MT_*}\mathbf g
\]
과 Maxwell 속도 측도를 직접 적분하면
\[
Q_a=G_{ab}(T_b-T_a),\quad Q_b=-Q_a,\qquad
G_{ab}=4k_Bn_an_b\frac{\mu}{M}\overline g\,\overline Q_{11}(T_*).
\]
\([G_{ab}]={\rm W\,m^{-3}\,K^{-1}}\)이다. 작은 상대 drift \(\mathbf U=\mathbf u_a-\mathbf u_b\)에서는
\[
\mathbf R_a=-K_{ab}\mathbf U+O(|\mathbf U|^3),\qquad
K_{ab}=\frac43n_an_b\mu\overline g\,\overline Q_{11}(T_*).
\]
열식은 무 drift 조건, drag 식은 drift 일차 조건이다. 이 둘을 유한 drift 모델로 조립하려면 \(O(U^2)\) frictional heating과 종별 분배를 같은 사건법칙에서 공급해야 한다.

\(T_a=T_b\) 또는 한 밀도가 0이면 열교환은 0이다. \(T_a>T_b\)이면 \(a\)종이 에너지를 잃고,
\[
\dot s_{\rm pair}=
\frac{G_{ab}(T_a-T_b)^2}{T_aT_b}\ge0.
\]
무한 target mass 극한에서 \(\mu/M\to0\)이므로 열교환은 약해진다. 이는 방향 산란과 열화의 질량 의존성이 다름을 보여 준다.

이 연결의 source 온도 범위는 \(50\le T_*\le50000\) K다. H/He source label의 isotope/state/mass mapping과 calibrated source uncertainty는 아직 지정되지 않았다. 구현은 별도 근거를 갖춘 \(\overline Q_{11}(T_*)\) 값을 입력받으며, 이번 단위에서 새 fit 평가나 계수 scan을 수행하지 않았다. 자세한 정규화·유도·원전은 [pair theory](pair_source/THEORY_KO.md)에 있다.

## 열용량·입자수·binding·비열적 에너지

Raw conservative mass/momentum/kinetic-energy source를 \(S_s,\mathbf R_s,E_s\)라 하면 종의 bulk \(\mathbf u_s\)에 대한 중심 에너지원은
\[
Q_s=E_s-\mathbf u_s\cdot\mathbf R_s+\frac12u_s^2S_s.
\]
Acceleration source를 \(\mathbf F_s=\mathbf R_s-\mathbf u_sS_s\)로 정의하면 같은 식이
\[
Q_s=E_s-\mathbf u_s\cdot\mathbf F_s-\frac12u_s^2S_s
\]
가 된다. 두 momentum convention을 섞지 않는다.

공통 thermal pool에서
\[
u_{\rm cal}=\sum_s n_s\epsilon_s(T),\quad
C_V=\sum_s n_s\,\partial_T\epsilon_s,\quad
Dn_s+\Theta n_s=\Gamma_s^{\rm th}
\]
를 쓰면
\[
C_VDT=Q_{\rm cal}-p\Theta-\sigma:\pi-\nabla\cdot\mathbf q
-\sum_s\epsilon_s(T)\Gamma_s^{\rm th}.
\]
단원자의 \(\epsilon_s=\tfrac32k_BT\)는 translational energy다. source가 nonthermal electron을 낳았다는 사실은 thermal \(\Gamma_s^{\rm th}\) 또는 \(Q_{\rm cal}\)을 자동 공급하지 않는다.

REC가 준위 population을 직접 진화시키면 excitation/binding energy는 그 population에서 계산한다. 같은 component를 equilibrium molecular caloric function에도 포함하려면 모델 선택을 바꿔야 한다. 구현은 같은 component ID의 두 소유권을 거절하며 population-derived account에는 독립 evolved RHS 대신 derivative witness만 반환한다.

Canonical transfer ID 하나는 두 reservoir에 반대 부호를 준다. Thermal/bulk/nonthermal kinetic energy, chemical binding, internal excitation, nuclear mass, retained/escaped radiation, escaping neutrinos, external work를 구분한다. WU의 elementary event compiler를 다시 구현하지 않고 이미 공급된 count/energy receipts를 소비한다.

공통 baryon bulk에 대한 압력은
\[
P_{b,ij}=\sum_s\bigl[P_{s,ij}+
\rho_s(u_s-u_b)_i(u_s-u_b)_j\bigr]
\]
로 합성한다. Drift tensor를 남긴 뒤 trace와 STF를 나눈다. 공통 온도·공통 속도 reduction의 실제 타당성은 선택 모델의 relaxation/source/Hubble 시간 및 관측량 오차로 따로 판정한다.

## 실제 검증과 보존한 실패

최초 source inventory12, H–He intake5, exchange13의 30개 단위검사는 실제 PASS였다. 별도 작성자의 독립 검토는 일반 유한 질량 입력에서 \(m_a+m_b\) overflow가 유한 교환량을 0으로 만들 수 있는 구현 오류를 발견했다. \(m_a=m_b=10^{308}\), \(\sigma_\ell=10^{-308}\)인 정적 반례의 정확한 \(\Delta p_x=-0.5\)를 보존하도록 질량비와 reduced mass를 스케일링했다. 실제 핵종 질량 영역의 과학 입력을 바꾸지 않은 API 경계 수정이다.

영향받는 5개 검사를 실행한 attempt04는 4 PASS / 1 FAIL이었다. 실패는 기존 synthetic exact-equality assertion의 \(-12\)와 안정화된 연산의 \(-12.000000000000002\) 사이 1 ULP 차이였다. 원 FAIL·source identity·비용을 남기고, 독립 정확값에 대한 \(8\,{\rm ulp}(12)\) roundoff bound를 명시했다. 같은 수정의 verification continuation에서 해당 한 method만 실행해 PASS를 얻었다. 물리 source tolerance는 변경하지 않았다.

최종 evidence coverage는 **31개 서로 다른 method**, 실제 method execution은 **36회**다. 원 실행 결과는 **PASS/PASS/PASS/FAIL/PASS**이며 FAIL을 덮어쓰지 않았다. 대수·source/implementation 검증으로 해석하며 전체 물리 공급자 승인을 뜻하지 않는다.

[실행 원장](evidence/validation/RESOURCE_LEDGER.json)의 측정 합계는 CPU **0.282464889 s**, wall **0.280453644998488 s**다. 이는 child interpreter 시작을 포함한 child 실행과 해당 구간 parent 비용이다. Parent startup/import·source hashing·START 저장·종료 후 로그 저장·provider/모델/IO 비용은 이 합계 밖이다. 전 과정 상한을 주장하지 않는다. Child의 RLIMIT_AS는 256 MiB다.

Implementation-validation envelope의 CPU8/wall30 s는 유지했고 repair_used=1, 같은 repair의 verification_continuation=1을 보존했다. 한 번의 oracle correction은 [VALIDATION_ADDENDUM_01](VALIDATION_ADDENDUM_01.json)에 이유·허용 method·횟수·중단 조건을 고정했다. HE101 예산으로 전가하지 않았다.

## 전체 DAG에서의 위치

현재 단위는 WU/REC supplier → HE source intake → 선택된 pair 교환·열/count interface까지의 연결을 구현했다. 물리적 mass/state/uncertainty binding, source-qualified DCS/joint law, 비열분포/stopping, 검증된 common-T/u reduction이 후속 의무다. [현재 DAG](DAG.json)는 이 로컬 진척을 87-node 중앙 DAG와 대응시키며 owner 상태와 consumer 진척을 구별한다.

HE101은 기존 owner의 **19/20, C8 PARTIAL_EXPORT, repair reserve0** 상태다. 기존 child PASS/FAIL/FAIL, exit0/-9/-9, CPU11.882829/wall11.985978921002243 s 및 PR100+CBA lineage CPU16.870803/wall17.108468335994985 s를 그대로 유지했다. 원 ledger의 실제 경로는 research/he_ang_finitemass_cba_20261025/evidence/execution/RESOURCE_LEDGER.json이다.

다음 실행은 실제 WU isotope/state/mass mapping과 한 선택 pair의 source-qualified \(\overline Q_{11}\) 값·오차를 연결하는 것이다. 전종 캠페인이나 HE101 export를 이 pair의 선행조건으로 추가하지 않는다. Joint ionization/angular provider와 nuclear daughter/stopping 채널은 각자 공급자·조건부 의존성을 유지한다.

