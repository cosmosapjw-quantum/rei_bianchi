# 다음 대화용 인계 — REI thermal assimilation, 2026-10-27

## 먼저 읽을 권위 자료

Repo는 **cosmosapjw-quantum/rei_bianchi**, 작업 branch는 **research/rei-thermal-assimilation-20261027**, draft [PR237](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/237)이다. 기준 PR236 HEAD는 **ee94bef85b56d879dc38f184856a5c613575e9e1**, 구현 동결 C5 commit은 **20b91606493fb7bad015c62fd62e2faa971faee0**이다.

최종 source commit·ZIP SHA256·Drive/Dropbox ID와 후속 전달 상태는 **delivery/FINAL_DELIVERY_RECEIPT.json**을 먼저 읽는다. 이 과학 source snapshot에는 사후 생성되는 자체 ZIP digest/ACK를 꾸며 넣지 않았다. 최신 전달 영수증과 HANDOFF는 같은 branch의 delivery commit에 있으며, source ZIP과 별도의 delivery metadata ZIP을 함께 보존한다.

다음으로 ADMISSION.json, REPORT_KO.md, STAGE_LEDGER.json, BUDGET_STATUS.json, review/FINAL_SCOPE_REVIEW.json, DAG_UPDATE_RECEIPT.json을 읽는다. 고정 출발 인계서는 [78f7ac58의 HANDOFF](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/78f7ac5864d5817ceb79b48cb5e298cc30006510/research/program_expansion_20261025/HANDOFF_KO.md)다.

- Working AGENTS blob: **6464cd96b7023e3e91e30246bc93650d4e435a10**.
- Central AGENTS blob: **429a5a13ee75b1222bc50627f8d5973d01dd21c4**.
- 마지막 중앙 확인: research/orchestration-sandbox-20261022, **12f6007a83a40d76f80574e41a5402676e81fc7a**, **27/88**.
- 작업 branch의 **32/88**은 아직 중앙에 merge하지 않은 별도 집계다.
- Native desktop cosmosapjw는 offline이었다. 게시되지 않은 local dirty state는 **UNOBSERVED**다.

재개 시 각 새 노드 전에 실제 최신 HEAD·AGENTS·병렬 반환·source 및 백업 ACK를 확인한다. 이미 한 전수 metadata 조사는 intake에 있으므로 그대로 반복하지 말고 새 delta부터 읽는다.

## 닫힌 유한 연구 단위

physmath-research-loop **R1–R10 및 C1–C10**의 이번 유한 단위는 **PASS_CONDITIONAL_NATIVE_COUPLED_LOCAL_SOURCE**로 채택했다. 실제 저장 PW19 HeII z2.479 배경에 제조 fast pool, 독립 지정 constant-in-energy nu, native REC RR/DR kinetic cooling·Planck Compton·실제 HE caloric caller를 연결한 25행 국소 source/JVP다.

| 항목 | 보존 값 |
|---|---|
| 실행 | 한 번, 118/118 PASS, repair/retry 0 |
| Algebra 최대 / 기준 | 3.3297273737548715e-16 / 2e-14 |
| FD 최대 / 기준 | 1.373105919989494e-10 / 2e-8 |
| FD 범위 | 한 방향, 두 step, 네 output map |
| 실제 HE logT residual | 0 |
| stdout SHA256 | 3f6e942336cb18cf1422ce4736984fb5d7f7d85ca1af39aa0f126748a0c66d99 |
| PREEXEC_MANIFEST SHA256 | 8f55b02555bc2ef1797efa77f54ed7c185275a384985f01afd5b626dcb4544b2 |
| code SHA256 | a84f318d66c11166db080f0f4db64b48f82ea5bc09abb87671c2ca44b162bbb6 |

독립 C5/C9·그림·최종 scope 검토를 재사용한다. 수치 통과를 실제 stopping/history/full-Jacobian 인증으로 확대하지 않는다. 원본 DAG 88개 ID·17개 edge·nested contract/gate를 보존했고, REC-COUPLED와 BASS 세 개 partial observation만 갱신했다. **완료수 증분 0, working32/88, central27/88, L4=false, global physical completion=null**이다.

## 유지할 물리 convention

\[
r=n_{\rm ref,0}a^{-3},\quad n_b=\beta r,\quad
Y=n/n_b,\quad \zeta=n_{\rm fast}/n_b,\quad w=u/n_b,\quad \ell=\log(T/{\rm K}).
\]

밀도 정규화는 처음 24행에만 적용하며 logT는 그대로 둔다. Eta clock에서는 25행 모두 1/H와 그 미분을 적용한다. General reference는

\[
\dot r+3Hr=R_r,\quad \dot n+3Hn=S,\quad
F_x=(S-xR_r)/r,\quad
\delta F_x=(\delta S-R_r\delta x-x\delta R_r)/r-F_x\delta r/r .
\]

고정 comoving reference에서는 \(R_r=0\)이다. Reference 입력의 species와 모든 reservoir tangent에도 \(\delta\beta\)를 포함한다.

\[
n_{e,\rm th}=n_b(qY-\zeta),\quad
\chi=(1+q)Y-\zeta,\quad
j=\nu\zeta,\ h=\nu w,\quad
F_{\log T}=\frac{(h+q_C-L)/(c_vT)-qR-j}{\chi}.
\]

Photo primary는 fast store로 들어가고, fast→bath는 수와 에너지를 함께 전달한다. RR/DR escaping photon과 CMB exchange는 signed external ledger에 한 번씩 기록한다. 단일 event/에너지 owner를 유지한다.

\(\nu=8.160348695705333\times10^{-18}\ {\rm s^{-1}}\)는 H와 수치만 같고 독립 매개변수다. **물리적 nu/provider/uncertainty는 null**이다. 배경은 실제 저장값이며 fast count/energy는 제조한 두 moment다.

Native REC124 pin은 **e6ecef7624e39bee66b39e09d99fe355f76e2eae**, HE pin은 **ac6042a6b0610b09d0576538767ee0299389a5eb**다. 공통 atomic/Mao 온도 범위는 100…1e6 K, PW19 HeII primary support는 0…49945.58 eV다. n/T 행 0,5,6과 tangent는 정확히 0이다. Native ThermalSources.coefficients를 사용하고, 기존 evaluate의 prompt-heat/all-electron 가정을 다시 넣지 않는다.

## 예산과 재사용

최종 **BUDGET_STATUS.json**과 전달 영수증을 읽어 임시 cap 복원 및 누적 debit 보존을 확인한다.

- Main **595.225063/600 CPU s, NO_MORE_IVPs**.
- Planning 원 cap **10**, presentation 원 cap **30**으로 복원한다. 이미 초과한 알려진 누계도 그대로 보존한다.
- PR219 bootstrap, 기존83, GRID044 opacity, PR221 조건부 결과, PR233 source, PR235 normalization, PR236 photo/JVP를 재사용한다.
- **새83 전구간, NCP, 기존 suite, 새 IVP, spectral quadrature를 자동 실행하지 않는다. 예산을 0으로 초기화하지 않는다.**
- HE101 reserve0와 V6 closed lease(119 RHS,7 J,3 FD pairs,38.853874599994015 wall s)를 보존한다.
- CR owner의 1c88 고정 반환은 R10+C6 **16/20**, controls **36/36**, 새 unit **0.701900185/30 CPU s**다. C7 primary224 RHS와 C9 admission은 그 경계에서 pending이었다. 해당 reservation을 REI로 전용하지 않는다.
- 원격·미측정·과거 미확인 비용은 **UNKNOWN_NOT_ZERO**다. 알려진 부분합을 전체 비용이라고 부르지 않는다.

## 다음 실제 연구점

1. 공급자가 실제 finite-time **\(J_N[\mu],Q[\mu]\)**를 자격화했는지 확인한다. 대상 energy support·T·density·uncertainty·derivative를 받아 조건부 nu를 대체할 수 있는지 판단한다. Energy-dependent kernel이면 추가 measure/moment를 유지한다.
2. CR의 tagged-fast HeIII ground capture는 thermal count·선택 thermal heat가 0이고 retained photon은 별도 port다. Source exposure가 없는 pulse-integrated count를 rate로 바꾸지 않는다. 최신 owner 반환을 정확한 상태·정규화·에너지 소유권으로 소비한다.
3. 같은 scenario의 BASS transport/native finite absorption/error radii와 VigilODE 25-state client를 연결한다. 기존 제조 512-map 결과와 V6 actual-point certificate를 전 history 보증으로 확대하지 않는다.
4. Whole-network/L4는 공급자 범위·미포함 event/secondary/radiation·physical uncertainty·source-matched history gate가 닫힌 뒤 별도로 판정한다.

관련 identity가 바뀐 부분만 최소 검사 계약으로 다시 검증한다. 새 unit은 입력·변경식·허용오차·budget·stop condition을 먼저 동결하고, 독립 검토 후 **expected-SHA non-force push·source ZIP·Drive/Dropbox ACK·DAG 갱신**까지 수행한다. 게시와 백업에 대한 사용자의 명시적 승인은 계속 유효하다.
