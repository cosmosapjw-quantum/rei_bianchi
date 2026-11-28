# HE38 독립 raw Maxwell–Grad quadrature 검증

## 판정

**PASS_SCOPED.** 새 finite-mass H1 component를 incoming Maxwell 분포와 infinitesimal Grad first variation의 원정의에서 직접 적분한 독립 oracle과 비교했다. Production의 닫힌 3×2 STF 계수나 species heat 식은 oracle에 복사하지 않았다. Oracle 결과 네 묶음을 모두 저장한 뒤에만 production module을 import하여 비교했다.

고정한 온도는 2000, 20000, 200000 K이며 질량은 physical proton/electron 값을 사용했다. 각 온도에서 electron/H0 두 incoming species의 서로 독립적인 STF 변화와 electron/H0/proton 세 output tensor를 비교했다. 전체 실행은 base3개와 가장 고온의 refinement1개다.

- 모든 실행의 최대 scaled discrepancy: **4.188289715045812e−10**
- 모든 nonzero coefficient·heat 진단의 최대 상대 discrepancy: **1.3463789240880918e−9**
- 사전 frozen gate: scaled 및 nonzero relative **1e−8**
- 고온 refinement를 채택한 최종 세 온도의 STF 최대 상대 discrepancy: **5.481164659263532e−12**
- 최초 attempt1 / 완료1 / 실패0
- 기존 suite replay0, IVP0, render0, benchmark0

이는 선언한 Newtonian common-T/common-bulk Maxwell 기준과 uniform original Jacobi angular law의 유한 수치 검증이다. Empirical H1 angular calibration, 유한 anisotropy의 양성 분포 폐쇄, 전역 적분오차 certificate를 제공하지 않는다.

## 독립성 및 물리 입력

읽은 기준은 HE38 CONTRACT.json, independent DERIVATION.md의 source-coordinate 정의, 새 component의 공개 API와 model.py다. Theory와 implementation을 작성하지 않은 별도 agent가 raw oracle를 작성했다. 닫힌 species 결과를 expected값으로 비교할 때만 production을 사용했으며 적분 단계는 독립된 raw_oracle.py에 있다.

상수는 계약에서 독립적으로 적었다.

- me = 9.1093837139e−31 kg
- mp = 1.67262192595e−27 kg
- mH = mp+me, total mass = mp+2me
- kB = 1.380649e−23 J/K
- eV = 1.602176634e−19 J
- I = 13.6 eV, a0 = 5.29177210544e−11 m

Oracle는 production의 rate 함수, transfer 평균 함수, event constructor, species heat/STF 함수 또는 donor moment evaluator를 호출하지 않는다. 비교 단계의 production identity는
e62606ffa4580a25a0097889c070423a084a28b2b19758a7a772d06cc338944f
이며 시작과 종료 시 전체 comparison package Python source hashes가 일치했다. 정확한 파일별 SHA256은 attempt의 START.json에 있다.

## 실제 적분

내부 단위는 me=θ=1이며 θ=kBT다. 질량비 mp/me는 유지하고 속도는 sqrt(θ/me)로 나눴다. 이는 물리 상수를 없앤다는 가정이 아니라 숫자 크기를 조절하는 단위 선택이다.

V는 각 성분 분산 θ/(mp+2me)의 Gaussian, g0는 상대속도다. 직접
v_e=V+[mH/(mp+2me)]g0,
v_H=V−[me/(mp+2me)]g0
를 구성했다. 두 STF 방향은 Frobenius norm1인 다음 행렬이다.

\[
Z_1=\frac{\mathrm{diag}(1,-1,0)}{\sqrt2},\qquad
Z_2=\frac1{\sqrt{28}}
\begin{pmatrix}0&1&2\\1&0&3\\2&3&0\end{pmatrix}.
\]

pi_s=n_s θ Z로 두었을 때 원 Grad 가중치는 내부 단위에서
\(w_s=(m_s/me)v_s^T Z v_s/2\)
다. 이 가중치를 raw net event pressure tensor에 직접 곱했다. 유한차분을 사용하지 않았다. Scalar rate와 heat의 first variation이 0인지도 같은 적분 결과에서 확인했다.

상대에너지를 E=I+θt로 치환한 뒤 Maxwell 상대속도 분포·relative speed·source cross section의 곱을 양의 measure
\[
e^{-t}\frac{t}{x+t}\,dt,\qquad x=I/\theta
\]
로 적분했다. 독립적으로 복구한 SI prefactor는
\[
A(T)=4\pi a_0^2 I\sqrt{\frac{8}{\pi\mu\theta}}e^{-I/\theta}
\]
다. 따라서 raw dimensionless rate에 A를 곱하며 heat에는 θA를 곱한다.

원래 transfer quantile
\[
\Upsilon=\frac{I}{1-u+uI/E},\qquad 0<u<1
\]
를 양의 Gauss–Legendre u quadrature로 적분했다. 닫힌 transfer mean, beta−theta alpha compression, 공유 energy split의 분석식은 사용하지 않았다.

각 U에서 original Jacobi g1/g2의 signed Cartesian 축6개씩을 모두 조합한 **36개 방향쌍**을 실제 생성했다. 이 g1/g2로 두 outgoing electron과 proton의 속도를 구성하고 \(m v_i v_j\)를 직접 평균했다. Incoming electron/H0 tensor를 직접 빼서 종별 net tensor를 얻었다. Outgoing conditional tensor의 유도된 간략식도 oracle에 사용하지 않았다.

### Quadrature와 exactness 범위

| 변수 | 실제 rule | 해당 observable의 성질 |
|---|---|---|
| COM V | GH3³ = 27 nodes | pressure×Grad가 V에서 최대4차이므로 Gaussian degree4 exact |
| Incoming g0 방향 | GL3 cosθ × uniform φ8 = 24 directions | 최대4차 구면 다항식 적분 |
| Outgoing g1/g2 방향 | signed axes6 ×6 =36 | pressure observable은 각 방향의2차까지; 독립 isotropic second moments를 정확히 나타내는 cubature |
| Radial t | Laguerre48, 고온 refinement72 | rational radial integrand의 유한 수치 quadrature |
| Transfer u | GL32, 고온 refinement48 | inverse-CDF의 유한 수치 quadrature |

Outgoing 방향을 36개로 적분한 것은 이 observable의 2차 모멘트까지에 대한 exact cubature다. 실제 angular density가 이산 방향이라는 물리 가정으로 바꾸지 않았다. Radial 및 transfer 적분은 exact quadrature라고 주장하지 않는다.

## 실제 오차와 refinement

| T K / radial×transfer | Rate 상대차 | Heat 최대 상대차 | STF tensor 최대 상대차 | H0+p 작은 합 상대차 |
|---|---:|---:|---:|---:|
| 2000 / 48×32 | 3.55e−15 | 5.05e−15 | 3.08e−12 | 2.71e−14 |
| 20000 / 48×32 | 4.00e−15 | 5.22e−15 | 1.74e−13 | 3.61e−14 |
| 200000 / 48×32 | 4.19e−10 | 4.19e−10 | 1.35e−9 | 4.18e−10 |
| 200000 / 72×48 | 1.71e−12 | 1.71e−12 | 5.48e−12 | 1.20e−12 |

높은 T에서 x가 가장 작아 radial rational integrand의 finite-order 수렴이 가장 느리므로 한 번의 hotter-case refinement를 사전에 고정했다. 두 고온 grid 사이 변화는 다음과 같다.

| 양 | 최대 dimensionless absolute 변화 | 전체 배열 norm 상대변화 |
|---|---:|---:|
| Rate | 1.87571e−10 | 4.17118e−10 |
| Species heat | 2.81204e−10 | 4.16823e−10 |
| Full STF responses | 1.32489e−10 | 2.70785e−10 |

위 변화는 실제 두 grid의 차이다. 정확한 연속해와의 rigorous upper bound가 아니다. 낮은 두 T는 추가 grid를 반복하지 않았으며 production과 raw 정의의 관측된 일치 및 degree4 angular/Gaussian exactness 범위만 제시한다.

STF 상대차는 각 output/input/direction tensor의 Frobenius norm으로 계산했다. Scaled gate는 component 오차를 max(1, expected tensor 최대성분)으로 나누었다. 작은 H0+p heat는 oracle에서 두 종의 직접 합을 취하고 production의 직접 small-combination 값과 별도 비교했다. 이 상대오차에 숨겨진 floor를 넣지 않았다.

## 구조적 0과 event 보존

모든 4개 case에서 관측한 최대값은 다음과 같다. Tiny zero는 상대오차가 아니라 선언한 gross scale로 정규화했다.

- Scalar rate first variation: 1.053e−17 이하
- Scalar heat first variation: 1.157e−16 이하
- Unperturbed STF: 8.882e−16 이하
- Total species heat와 −I×rate 일치: 6.107e−16 이하
- 실제 outgoing event들의 kinetic energy + binding defect: 1.055e−15 이하
- 실제 event momentum scaled defect: 1.066e−14 이하

Momentum의 scale은 내부 단위에서 max(1, incoming COM momentum norm)이다. Incoming COM momentum0인 node를 상대값0으로 나누지 않는다. 이 검사는 oracle가 실제 생성한 사건에 적용한 기록이며 이전 theory108 exact event suite를 재실행한 것이 아니다.

## 실행·보존·자원

실행 명령은 python /tmp/he38_raw_controls/launch.py였다. 런처가 one-thread 환경과 RLIMIT_CPU30s / RLIMIT_AS512MiB를 설정했다.

- Child 전체 user CPU5.473718s + system CPU0.503833s = **5.977551s**
- Child wall5.987988759s
- Raw runner 내부 CPU5.135023996s
- Maximum RSS56916KiB = **55.58203125MiB**
- Return code0, stderr 빈 문자열

내부 timer와 process 전체 시간을 구별했다. 성능 비교나 speedup benchmark를 수행하지 않았다.

실제로 계산한 것은 raw quadrature4개, response tensor blocks48개, radial×COM×incoming-angle nodes139968개, outgoing velocity triples7838208개다. 각 triple은 동일 사건의 두 electron과 proton 속도를 뜻한다. 세 base온도의 response36블록과 고온 refinement12블록을 중복 없는 서로 다른 numerical grid 실행으로 구별했다.

각 NPZ에는 최종 tensor뿐 아니라 radial node별 unperturbed pressure, direct linear pressure 및 rate variation과 quadrature nodes/weights를 저장했다. 수백만 개의 모든 event velocity array를 별도로 저장했다고 주장하지 않는다. 이들은 source/contract/hash가 고정된 생성 경로로 재현 가능하며 실제 실행의 부분 결과는 per-case NPZ와 receipt에 있다.

권위 파일:

- CONTRACT.json: 실행 전 온도·quadrature·gate·budget
- raw_oracle.py: 독립 raw 정의 적분
- run_oracle.py: raw 저장 후 production 비교
- launch.py, LAUNCH_RECEIPT.json: 실제 hard resource limits 및 process 결과
- attempts/attempt_001/START.json: 실제 source·comparison source SHA256
- attempts/attempt_001/*npz 및 *_RECEIPT.json: create-only 개별 결과
- attempts/attempt_001/RESULT.json: 모든 오차·counts·refinement

최초 attempt를 수정하거나 삭제하지 않았다. 모든 gate가 충족되어 추가 수치 실행은 하지 않았다. Parent의 129T diagnostic과 plot은 이 실행 집계에 포함하지 않는다.


## 게시 경로 이식성 교정 F2 — 새 과학 실행 0

원래 실행된 runner는 /tmp/he38_implementation을 비교 대상으로 고정했고 launcher는 attempt_001을 사용했다. 이 파일들과 실제 START/RESULT/NPZ/launch receipt는 변경하지 않았다. 이전 report와 manifest도 history/에 보존했다.

별도 portable/launch.py와 portable/run_oracle.py가 --implementation-root, --output-root, --attempt를 필수로 받는다. 복원된 unit/components/finite_mass를 지정할 수 있으며 기존 attempt와 launch identity는 exclusive 생성으로 거부한다. 원 raw_oracle와 frozen CONTRACT의 SHA256을 검증하고 30CPU s/512MiB/one-thread 제한을 유지한다.

상태는 PREPARED_NOT_SCIENCE_EXECUTED다. 새 파일에 대해 static compile, --help 및 quadrature/comparison/refinement의 세 loop AST 동일성을 확인했다. 원 executed 파일·receipt15개의 hash가 그대로임을 확인했다. 이 교정으로 새 numerical case를 실행하지 않았다. 구체적인 복원 경로 명령은 portable/README.md, 수정 근거와 정적검사는 PORTABILITY_REVISION.json 및 PORTABILITY_STATIC_VALIDATION.json을 따른다.
