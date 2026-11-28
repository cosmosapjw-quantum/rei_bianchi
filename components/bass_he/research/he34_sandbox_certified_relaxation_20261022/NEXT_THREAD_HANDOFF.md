# 다음 연구 스레드 인계 — HE34-SCR 이후

다음 요청문을 사용할 수 있다. 최종 science pin/archive의 값은 `delivery/S2_ACK.json`, 최신 게시 metadata는 PR88 head에서 읽는다.

```text
$physmath-research-loop로 BASS_HE HE34-SCR 완료 상태에서 이어가라.
workflow1.0.0 / approval0.2를 유지한다.
repo: cosmosapjw-quantum/BASS_HE
branch: research/he34-sandbox-certified-relaxation-20261022
PR: https://github.com/cosmosapjw-quantum/BASS_HE/pull/88
unit: research/he34_sandbox_certified_relaxation_20261022
계산 source pin: 1a07166434a2a9ede1464bcdc465cba3088bb795
최종 science commit/tree/archive SHA/provider ID: unit/delivery/S2_ACK.json

먼저 README.md, RESULTS_KO.md, CONTRACT.json, DAG.json,
RUN_RECORD.json, NEXT_DAG.json, theory/SCOPE_AND_DEPENDENCIES_KO.md,
delivery/S2_ACK.json, CODEX_HANDOFF.md를 읽어라.
verify_saved.py로 현재 code/input/output의 receipt hash만 확인한다.

HE32 원 DAG30/30은 계속 완료다. 392nominal+2angular guards,
8핵종21상태 prescribed-UV photo+caseA RR, 평균 z20→2,
그림6쌍/394NPZ와 receipt 및 원 archive를 재사용한다.
기존 matter stress는 nonbaryonic이고 HE32 gas pi_b=0이다.

HE33은 prescribed-rate source-free gas pressure mechanics의 기초를 완료했다.
HE34-SCR은 constant chi=nu_pi/H, Q=j=0, 저장 S(N)의 정의된 선형 보간에 대해
초기층을 보존한 축약과 연속계 residual/contraction error bound를 구현했다.
고정1e-6 r/logp 오차 기준에서 chi10/100은 거절,1000/10000은 수용했다.
이 연속계 bound와 binary64/구적 검증을 구별하며 machine interval proof를 주장하지 않는다.

중성 H1/He4 common-T=20000K first-Sonine 점성은 별도 결과다.
2x2 선형계의 양의 유리식 축약은201저장점에서 상대차6.4653e-16로 확인됐다.
chi_match=p_neutral/(eta H)는1.6671e4→1.5527e-3이며
전체 gas closure 또는 전 구간 fast-relaxation 인증이 아니다.
mechanical control의 prescribed chi에 이것을 자동 대입하지 않았다.

PR87 Lorentz unit은 별도 경로/pin0868889acebeb4d9b70d38313a9a694d12bf8766이다.
그 순간 Grad projection rate와 우리의 저주파 p/eta matching,
처방 mechanical nu_pi를 서로 다른 정의로 유지한다.

새 단원의 첫 작업은 NEXT_DAG의 B1과B2:
B1 pair/domain/moment inventory, finite-mass/charged exchange와 pressure-relaxation matrix,
B2 Q/J/R_part 및 SI/normalization/ionic-potential/energy-owner/isotope adapter다.
B1+B2→B3 closure validity→B4새coupled gas pilot→B5metric feedback 순서를 지킨다.
추가 종·CI/DR/CX·thermal/source evolution의 범위를 별도 계약으로 고정한다.
미확보 reactive STF source를 isotropic illumination만으로0이라고 두지 않는다.

PHYS79/THERM01/REI221/PR87의 기록된 intake 이후 직접 관련 변경부터 조사한다.
모든 repo/대화를 다시 전수 조사했다고 쓰지 않는다.
완료 IVP/benchmark/그림을 재실행하지 않고 변경된 dependency만 검증한다.
새 과학 단원은 별도 unit/DAG로 진행하고 매 단계 백업/게시/진척/다음DAG를 표시한다.
현재 sandbox에서 승인된 작은 유도·코드·검산을 먼저 완료하고
Codex 실행자용과 다음 연구 스레드용 두 handoff를 계속 제공한다.
```

## 현재 상태를 과장하지 않기 위한 경계

모든 불안정 동위원소, 음이온, 분자 또는 fully reactive19채널 핵반응망은 완료되지 않았다. B1의 중성 H1/He4 부분 해법과 B2의 다른 repo donor 산출물은 전체 B1/B2 완료를 의미하지 않는다. 모든 B1–B5 full-node completion evidence는 열린 상태다.

이번에 실제 새로 실행한 저장배경 full-moment reference는11 histories/2200 interval solves이며 이것은 새 prescribed mechanical state다. HE32 cosmological IVP 반복은0이다. source-stage synthetic prototype16회(첫 serialization 실패 포함)와 별도 reviewer controls는 별도 장부에 있다. 새 그림은2쌍이고 기존HE32그림6쌍의 재렌더는0이다.

사용 가능한 source·코드·실행 근거가 있는 곳부터 이어가라. 새로운 근거가 필요할 때는 과거의 모든 자료를 다시 수집하지 말고 현재 주장에 필요한 범위를 명시한다. 현재 성능 수치10.69 및1.29는 선택한 대조법과 sandbox workload의 측정값이며 일반적인 최적 가속비가 아니다.
