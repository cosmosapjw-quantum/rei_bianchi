# REI source-age 양의 Duhamel 기준해: C6–C8 (2026-10-16 KST)

## 물리적 연구 범위와 실제 기준

기준 native source는 `rei_bianchi` PR #166 HEAD `553ce556d9f8662290c000ec675c7e6007c9d895`, 실행된 PR150 native `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`. 실제 native NCP 출생 코호트 자료는 기존 이중 백업 ZIP SHA256 `2ebab11829b793eb19a0b91e5d04a3a8637e346e456ac0931c372585ef7e21de`에서 읽었다. 원본 Python/Rust source, gamma/heat ledger, accepted checkpoint는 수정하지 않고, 이 단계에서는 NCP 실행하지 않았다.

R5/C5 선행 연구: 고정 source와 불투명도에서는 `N_new=N_old exp(-τ)+S φ1(-τ)`, `φ1(-τ)=(1-exp(-τ))/τ`. PR166 q_ref=0의 n8→16·n16→32 전체 잔류량비 `54.45978`과 `10.33099`은 **단일 κ** 가정 시 각각 `τ=150.0968`과 `193.6604`를 요구한다. 두 값을 하나의 광학깊이로 일치시킬 수 없으므로, frozen slab 공식은 PR166 nonlinear 해의 실증적 대체물이 아니다. 마지막 코호트 기여율이 n8,n16,n32에서 `99.9884%,99.9633%,99.6222%`임은 늦은 출생 광자 경계층의 매우 강한 징후이다.

## 새로운 조건부 이론

`x=ln(a/a_ref)`에서 원자 stock과 photon energy가 처방된 경우 `N'=j(x)-κ(x)N`, `κ=κ_HI+κ_HeI+κ_HeII≥0`, `j≥0`이다. Duhamel의 양의 정확해는

`N(x)=N0 exp[-H(x)]+∫_0^x j(y)exp[-(H(x)-H(y))]dy`,
`H(x)=∫_0^x κ(z)dz`.

각 이온화 종의 photon count `A_i=∫κ_i(x)N(x)dx≥0`, 그래서 `N(x)+ΣA_i=N0+∫j`. 광자 에너지가 한 화학 substep 동안 `E`로 고정되는 조건이면 `E(N0+∫j-N)=Σ_i χ_i A_i+Σ_i(E-χ_i) A_i`가 성립한다. FIT threshold와 physical binding χ는 서로 다른 소스이다. 이 에너지 ledger는 **제조된 고정 E 모델 안의 항등식**으로, 동적 signed geometry/shear work나 Grackle thermal validation이 아니다.

이름 붙인 manufactured case: `x∈[0,1]`, `j=1+0.3x` photons/H/dln(a), `N0=0.002/H`, `E=80eV`; `κ_HI=95+35x`, `κ_HeI=35+25x`, `κ_HeII=85 Θ(x-0.73)`. 정확한 `H(x)=130x+30x²+85max(0,x-0.73)`. 단면적·중성분율을 원래 Grackle에서 가져온 것이 아니라 **독립적인 양성성·수치 분석용 제조 함수**이다. `x=0.73`의 날카로운 He II 이벤트는 물리적 threshold crossing을 시험하기 위한 모형 이벤트이고 cosmological calibrated hazard는 아니다.

서로 독립적인 두 경로를 비교한다. (1) 이 정확한 `H(x)`에 대한 SciPy `quad` 기반 source Duhamel 적분, 이어 종별 `κ_i N` nested adaptive quadrature. (2) 각 구간에서 frozen midpoint `j,κ_i`에 대해 exact exponential/φ1 update, event-aligned 또는 미분할, 양의 2-half error indicator를 이용하는 adaptive controller. RK trial에서 negative N을 임의 clip하지 않는다. 과거 DOP853 음수 내부 stage는 완전히 다른 explicit solver 경로에서 관측된 것이므로 고정-모형 positive 경로의 성공이 원래 PR166의 291-call failure를 수리한 것은 아니다.

## 실제 C6–C8 실행 결과

샌드박스 Python 3.13 기반 **34/34 unittest PASS**: C5 선행17 + 신규 17. 첫 신규 source 및 regression 구현이 모두 통과한 최종 로그는 `evidence/c8_34tests.log`. 실제 코드와 테스트는 `src/duhamel_diagnostics.py`, `tests/test_duhamel_diagnostics.py`. 전체 benchmark source와 JSON은 `src/run_duhamel_study.py`, `results/duhamel_diagnostics.json`, 그래프는 `figures/duhamel_refinement.png`.

독립 Duhamel 기준 생존 `N(1)=0.004727055831538651/H`, HI/HeI/HeII absorbed 각각 `[0.7318932975959715,0.30632880333250406,0.1090508432399853]/H`; photoheat `68.36310432411628 eV/H`, binding `23.418731209360587 eV/H`. QUAD 기반 photon mass residual `4.44e-16/H`, energy residual `4.26e-14 eV/H`.

**동일 총 rate/source 평가 수**로 보정한 비교 (event split: panel당 n개씩 2개 panel, unsplit: 2n개 전체):

| 총 evaluation | split φ1 상대 N오차 | unsplit φ1 상대 N오차 | midpoint impulse 상대 N오차 |
|--:|--:|--:|--:|
|16|1.67365e-4|3.50191e-4|9.96745e-1|
|64|1.89230e-5|5.53816e-5|4.91666e-1|
|256|1.27745e-6|4.32308e-6|4.65458e-2|
|512|3.20697e-7|1.09608e-6|1.1930e-2|

Event-aligned φ1의 마지막 인접 수렴 차수는 1.97642이고 이 예제에서 약 2차에 접근한다. 이 수렴 차수는 구간 내 smooth source/rates 및 정확한 event 위치에 종속한다. 3종 binding/photoheat에도 별도 잔차를 저장했다. 모든 φ1 discrete scheme은 음의 number/absorption을 생성하지 않았으며 tested photon/energy ledger 최대 잔차는 floating precision이다.

`adaptive_positive(rtol=1e-8)`는 5,166 accepted halfsteps, 2,581 rejected panels을 사용하여 N 절대오차 `9.4871e-11/H`, photon residual `2.22e-16/H`, energy residual `1.42e-14 eV/H`를 얻었다. **512 uniform evaluations보다 고비용**이다. 로컬 coarse/fine 추정치는 global error certificate가 아니라서 승인 문턱을 과장하지 않는다. Source shape/time interpolation, actual spectral attenuation 및 nonlinear gas의 오류는 모두 미래의 별도 항목이다.

### 독립성·검토 및 보류

- 원본 실제 native 8/16/32가 격자 증가에도 생존량이 늘어나는 현상은 정량적으로 다시 관찰했고 single constant κ 가설은 실제 두 비를 동시에 재현하지 못했다.
- 독립 양의 이론적 reference는 **prescribed** `j(x),κ_i(x)`와 fixed E에 대해서 검증됐다.
- PR166 source-matched full `PreparedAbsorption`/Grackle/MD14 coupled independent reference는 이 단계에서 **NOT_RUN**; 원래 DOP853 internal trial 실패는 여전히 `HOLD`.
- 최근 별도 PR167 old/newborn photon splitting, PR168 RR/DR midpoint, HE25/26, bass_cr C21/C21B는 소스와 scope를 대조해 중복 계산하지 않았고 다른 repo source는 수정하지 않았다.
- Wolfram R5 초도 항등식 `{0,0,1,0}`는 기록에 재사용한다. 이번 Wolfram 연결은 `UNAVAILABLE` 후 evaluator 오류로 신규 CAS 검증 `NOT_RUN`이다. 독립 QUAD/tests는 실제 실행 근거로 충분하다.
- `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`, native subagents `NOT_RUN`; 별도 native delegation tool 없음.

관련 원전: Mellema et al. C2-Ray https://arxiv.org/abs/astro-ph/0508416; Friedrich et al. 2012 He multifrequency C2-Ray https://arxiv.org/abs/1201.0602; Pawlik & Schaye 2011 TRAPHIC https://arxiv.org/abs/1008.1071. 원전의 포톤 보존 및 시간평균 단면적 방법을 인용하는 것이며, 이번 독립 φ1 reference의 논문상 novelty 검증을 의미하지 않는다.

## 다음 실제 native 작업

동일 source/clock/geometry state를 공유하고 원래 `PreparedAbsorption`의 positive atom/node decomposition을 유지하는 **PR166 source-matched continuous independent reference**가 다음 READY. `source_matched_solver.py`는 내부 RK trial에서 invalid state를 원래 point RHS로 전달하므로, 단순 tolerance 완화/negative projection 대신 원래 node별 `N=e^z` logarithmic/exponential positive representation 또는 semigroup splitting을 구현해야 한다. Empty support는 exact zero invariant lane, positive occupied supports만 transform한다. Nonlinear moment closure, native HHe gas implicit chemistry와의 source-matched parity와 original fixed-reference q must be checked by independent full-state comparator; NCP 서브프로세스는 별도 Codex 인계.
