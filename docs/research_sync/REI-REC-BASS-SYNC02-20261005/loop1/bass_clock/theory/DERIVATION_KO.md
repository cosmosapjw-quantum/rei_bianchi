# BASS-REI-CLOCK01: 동일한 opacity cell의 세 clock 적분

이 작업은 BASS에 이미 있는 proper electron density → normal-ray Thomson rate → visibility 계산에서 좌표 단위를 명시한다. 원자 provider, recombination 계수, implicit chemistry stepper 및 cold-Thomson 승인 범위는 변경하지 않는다.

## 정의와 단위

metric convention은 (−,+,+,+)이며 c를 유지한다. 기존 BASS의 normal-clock rate는

\[
q_t=c\sigma_T n_e^*D,\qquad D=\gamma(1-\boldsymbol\beta\cdot\boldsymbol e).
\]

여기서 \(n_e^*\)는 material frame의 proper density(m⁻³), \(t\)는 normal ray seconds이다. \(D\)는 upstream `ElectronState`/`ReiOpacityCell` 경계에서 한 번 반영된다. 원자 반응 source clock의 \(1/\gamma\)와 ray의 D를 혼동하지 않는다.

양의 dimensionless a로 \(dt=a\,d\eta\)를 정의하고 \(\chi=c\eta\)를 conformal length(m)로 정의하면

\[
q_\eta=a q_t\quad[\mathrm{s}^{-1}],\qquad
q_\chi=\frac{a}{c}q_t=a\sigma_Tn_e^*D\quad[\mathrm{m}^{-1}].
\]

세 표현 모두 \(d\tau=q_tdt=q_\eta d\eta=q_\chi d\chi\)이다. FLRW rest-frame 극한 \(D\to1\)에서 \(q_\chi=a n_e\sigma_T\)로 복원된다. CAMB `symbolic.py` 공개 문서는 opacity를 `a n_e sigma_t`로 기술한다. 본 문서의 c 포함 seconds/meters 변환은 위 정의로 직접 유도했으며 CAMB의 모든 내부 단위/physics를 이 비교만으로 검증했다고 주장하지 않는다.

## 정확한 이산 계약

입력 normal rate \(q_{t,i}\)는 물리적 cell마다 상수로 고정한다. 대응 좌표 edge가

\[
\Delta t_i=a_i\Delta\eta_i=(a_i/c)\Delta\chi_i
\]

를 만족하면 cell depth \(d_i=q_{t,i}\Delta t_i\)가 같다. 같은 \(\tau_{\mathrm{tail}}\ge0\)를 주었을 때

\[
\tau_i=\tau_{\mathrm{tail}}+\sum_{j\ge i}d_j,\quad
S_i=e^{-\tau_i},\quad
P_i=S_{i+1}\big[-\operatorname{expm1}(-d_i)\big]
\]

이므로 세 clock의 edge optical depth, edge survival, cell probability가 같다. 또한 \(\sum_iP_i+S_0=e^{-\tau_{\mathrm{tail}}}\)이며 유한 구간을 unit probability로 다시 정규화하지 않는다. `expm1`과 backward 누적은 원래 host 적분기를 그대로 사용한다.

clock별 probability density의 단위와 값은 다르다. \(g_\eta=a g_t\), \(g_\chi=(a/c)g_t\)이며 좌표 변경 후 peak height가 같다는 주장은 성립하지 않는다.

## a가 cell 내부에서 변할 때

caller가 실제 mapping을 적분하여 \(a_{\mathrm{eff},i}=\Delta t_i/\Delta\eta_i\)를 제공하면 frozen \(q_{t,i}\)에 대한 cell integral은 동일하다. 이는 \(a_i\)를 endpoint/midpoint 값으로 넣는 것과 구분된다. 예를 들어 \(a(\eta)=1+\eta\), \(t=\eta+\eta^2/2\), edges \(\eta=(0,1,3)\)이면 정확한 effective factors는 \((1.5,3)\)이고 endpoint factors \((1,2)\)는 잘못된 depth를 만든다. native test가 이 반례를 실행한다.

그러나 \(q_t\)도 실제 cell 내부에서 변하면 \(\int a(\eta)q_t(\eta)d\eta\)는 일반적으로 \(a_\mathrm{eff}q_{t,i}\Delta\eta\)와 같지 않다. 이 API의 정확성은 선택된 frozen opacity surrogate의 cell integral/edge 값에 한정된다. 실제 연속 history에 대한 quadrature 오차, interpolation 오차, peak 위치 및 높이, cosmological history 정확도는 별도 검증 대상이다. effective factor를 사용해도 cell 내부 실제 visibility profile이 정확히 재구성되는 것은 아니다.

## Native 경계와 실패 규약

`RayClockGrid`는 normal seconds, conformal seconds, conformal meters를 서로 다른 variant로 강제하고 conformal 경우 cell마다 a를 받는다. normal rate 배열을 재사용하므로 D, a⁻³ 또는 Q를 추가하지 않는다. nonfinite/음수 input rate는 변환 전에 거부하여 작은 음수가 underflow로 −0이 되는 bypass를 방지한다. a는 finite이고 엄밀히 양수여야 한다. a 개수 mismatch, 변환 overflow 및 양의 값이 0으로 사라지는 underflow는 명시적 오류다. 특히 vacuum q=0이어도 invalid a 및 물리적 Δt 변환 오류를 통과시키지 않는다.

원래 integrator가 grid/rate/tail validation 및 expm1 probability를 소유한다. 새 wrapper는 원래 파일을 수정하지 않고 해당 함수를 호출한다. 새 API는 inferred background/clock-origin authority를 제공하지 않으며, caller가 같은 physical cell의 대응 edge를 준비해야 한다.

## 실제 검증과 한계

- 최초 missing-module E0432 실패를 보존한 후 새 native 모듈을 구현했다.
- scoped actual-host test 30개가 통과했다. 기존 visibility/REI bridge/legacy dispatch 20개와 새 contract 9개/API 1개다.
- 실제 모듈을 링크한 native probe에 151개 case를 공급했다. 144개 valid coordinate cases는 48개 동일 physical grid의 세 clock이며, 나머지 7개는 invalid 입력이다.
- 별도 Python Decimal70 oracle에서 5001개 check가 통과했다. 세 clock 결과 간 최대 절대차는 2×10⁻¹⁸이다.
- 확률 최대 절대 oracle 오차는 약 1.44×10⁻¹⁶, survival은 약 1.61×10⁻¹⁶이다. opaque case에서 f64 survival/probability가 0으로 underflow하므로 전체 maximum relative error=1인 항목이 있다. 이는 사전 고정한 probability absolute tolerance 2×10⁻¹⁴ 내에서 평가했으며 상대오차 전역 인증을 하지 않는다.
- 전체 BASS crate 빌드 및 우주론 production evolution은 수행하지 않았다. 구현에는 새로운 dependency가 없다. independent decision review는 root가 별도로 수행한다.

근거 상태: 변환 및 cell invariance는 **derived**, native 경계는 **implementation-verified**, Decimal 비교는 **numerically checked**. finite-temperature/spectrum 승인과 full BASS kinetic coupling은 **unresolved / outside this change**이다.
