# RUN15: spectral edge support의 유도와 검증 범위

이 문서는 RUN13의 보존된 원자 공급자·prescribed BASS121 SIGNED_MINUS geometry·gas initial condition을 바꾸지 않는다. 단위는 SI를 기본으로 하고, 광자 에너지는 원래 source의 eV 표현을 그대로 사용한다. \(c=299792458\,\mathrm{m\,s^{-1}}\), \(k_B=1.380649\times10^{-23}\,\mathrm{J\,K^{-1}}\), \(1\,\mathrm{eV}=1.602176634\times10^{-19}\,\mathrm{J}\)이며 자연단위로 설정하지 않는다. Metric convention은 \((- ,+,+,+)\)이다. 이번 고정 source의 Planck shape에서는 \(\hbar\)를 포함하는 공통 정규화가 원래 native cell M0에 이미 들어 있으므로 M0를 재정의하지 않는다.

## 1. 동일한 물리적 시험과 서로 다른 수치 매개변수

\(X=\ln(a/a_{\rm ref})\), \(a_{\rm ref}=1/21\), \(X\in[0.7,0.7004]\), 160 birth samples, GL8, native atomic providers, 10,000 K manufactured chemical IC를 유지한다. Source blackbody temperature는 50,000 K이며 gas IC temperature와 다르다. Owner가 사용한 정확한 eV 변환 몫 \((1.380649\times10^{-16}/1.602176634\times10^{-12})\,50000\)을 보존한다.

RUN13의 m=1,2는 첫 spectral cell의 유한 refinement 이력이다. 소실 전에 새로 실행된 optical n=4,6,8은 광학깊이 core의 Gauss node 수이다. 이를 uniform m=4 또는 서로 같은 refinement parameter라고 부르지 않는다. 실제 native uniform m=4는 이번 요청에서 실행하지 않았다.

H binding energy 13.598434599702 eV, H fitting edge 13.6 eV, manufactured D gate 13.602134599702 eV를 구분한다. D 공급자는 threshold-gated H-equality approximation이며 isotope-specific experimental cross section으로 해석하지 않는다.

## 2. Monotone path의 조건

양의 achromatic redshift path에서 \(E(X)=R(X;X_b,\mu)E_b\), \(R(X_b)=1\)이다. 종단의 \(R\le1\)만으로 중간 경로의 단조성을 증명할 수 없다. 기존 축대칭 geometry의 longitudinal energy fraction을 \(w\in[0,1]\)라 하면

\[
q=-\frac{d\ln E}{dX}=1+b_X(3w-1).
\]

따라서 전 구간에서 \(-1/2<b_X<1\)이면 모든 방향에 대해 \(q>0\)이다. 실제 구현에서는 원래 geometry와 그 도함수를 평가한다. Endpoint의 제조 상수 \(e^{-0.0004}\)로 native ray ratio를 치환하지 않는다.

## 3. Source integral과 좁은 광학깊이 층

\[
g(E_b)=\frac{E_b^2}{\exp(E_b/(k_BT_{\rm source}))-1},\qquad
M_0^{(1)}=\int_{E_{\rm cell,lo}}^{E_{\rm cell,hi}}g(E_b)\,dE_b.
\]

각 birth/ray의 원래 first-cell 수 \(N_{b\mu}^{(1)}\)를 유지한다. 정의된 gas 경로를 고정했을 때 sub-H-fit survivor는

\[
P_{<H}[n]=\sum_{b,\mu}\frac{N_{b\mu}^{(1)}}{M_0^{(1)}}
\int_{E_{\rm cell,lo}}^{\min(E_{\rm cell,hi},E_{H,\rm fit}/R_f)}
g(E_b)e^{-\tau(E_b;b,\mu)}\,dE_b.
\]

적분 구간이 비면 기여는 0이다. 이는 source measure의 response integral이며, 이미 진화한 survivor에 임의 보정을 더하는 절차가 아니다.

H threshold crossing까지의 optical depth는

\[
\tau_H=\int_{X_b}^{X_c}\frac{c n_{\rm HI}(X)\sigma_H(E(X))}{H(X)}\,dX
=\int_{E_{H,\rm fit}}^{E_b}
\frac{c n_{\rm HI}(X(E;E_b))}{H(X(E;E_b))q(X(E;E_b))}
\frac{\sigma_H(E)}{E}\,dE.
\]

균일한 양의 하계 \(\lambda_{\min}\)가 있으면 \(\tau_H\ge\lambda_{\min}(E_b-E_{H,\rm fit})\)이다. 따라서 생존 기여의 에너지 폭은 대략 \(1/\lambda\)이며, 이 폭을 보지 못하는 넓은 첫 cell의 낮은 차수 quadrature는 작은 sub-H 성분을 놓칠 수 있다. 전체 survivor의 상대 안정성이 이 작은 성분의 수렴을 대신하지 못하는 이유다.

광학 core 밖에서는 \(\tau_{\rm full}\ge\tau_H\)인 양의 흡수 조건을 이용해 tail을 상계한다. D-active 영역을 수치 합에서 버렸다고 끝내지 않고, 그 미계산 영역의 양의 upper contribution을 별도로 기록한다. Lower bound나 rigorous interval을 주장하려면 core integration error와 부동소수점 방향 반올림도 함께 통제해야 한다.

## 4. 세 오차를 분리한다

1. **ODE tolerance sensitivity.** 같은 packet·event grid·state dimension에서 standard/tight를 비교한다. 두 해의 작은 차이는 엄밀한 실제 해 오차 한계가 아니다.
2. **Energy integration/refinement.** 같은 gas 경로·birth/angle/rates에서 energy node 수를 바꾼다. 서로 다른 n의 coupled native trajectory 차이에는 gas feedback 변화도 들어 있다.
3. **Threshold classification 및 작은 bin.** H-fit과 H-binding을 별도의 observable로 둔다. Terminal binding-edge의 birth-energy preimage를 partition에 넣지 않은 기존 n4/n6 native 결과에서 binding–fit bin은 전체 sub-H와 같은 수렴 지위를 받지 못한다.

새 postloss fixed-gas 진단은 원래 saved m2 tight 13-knot 경로와 standard 18-knot 경로를 구분한다. 이 둘의 차이는 서로 다른 PCHIP 정의 경로의 민감도이며 same-grid solver tolerance 비교가 아니다. Actual IVP의 knot 사이 gas 경로 오차와 continuous-source nonlinear feedback은 별도 미완료 항목이다.

## 5. Quadrature 정리의 전제와 수치 증거

양의 measure에 대한 n-node Gaussian rule은 해당 moment functional의 다항식 차수 2n-1까지 exactness를 갖는다. GL64의 양의 discrete measure에서 구성한 Stieltjes/Jacobi rule의 exactness를 원래 continuous Planck measure의 rigorous bound로 자동 승격하지 않는다. 일반적인 Gauss remainder에는 충분한 도함수 및 panel regularity가 필요하다. Threshold뿐 아니라 \(E_b=E_{\rm edge}/R(X_k)\)인 gas/geometry knot preimage도 response regularity에 영향을 준다. PCHIP는 C1이며 일반적으로 second derivative가 knot에서 점프한다.

이 때문에 두 유한 표본에서 continuum asymptotic order를 확립하거나 Richardson denominator 15를 자동 사용하지 않는다. Conservation contrast

\[
\Delta P+\sum_a\Delta A_a-\Delta B=\Delta R
\]

는 ledger의 항등식이다. 작은 residual은 spectral error certificate가 아니다.

## 6. 보존 상태에 따른 주장 제한

RUN13 원본333 파일과113 source/input은 Git와 재다운로드한 Drive ZIP에서 다시 byte-identical로 확인됐다. 소실 전 새 RUN15 네 IVP의 완료 수치는 실제 실행 출력에서 회수했지만 raw state/packet bytes는 현재 없다. 이 수치와 그 기대 hash는 transcript evidence로 보존하며 재시작 가능한 endpoint로 채택하지 않는다. 일부 소스와 두 enclosure JSON은 소실 전 SHA와 정확히 일치하도록 회수됐다. 원래 누락된 tests와 source를 추측하여 exact recovery로 표시하지 않는다.

Postloss native crate는 확실하게 회수된 원래 production implementation prefix를 별도 provenance와 새 wrapper로 빌드한다. 새 fixed-gas Python 진단도 독립된 새 source identity를 갖는다. 이 두 산출물의 현재 byte identity, 실제 명령, 결과와 한계를 최종 manifest와 receipt로 검증한다.

## 7. 원래 DAG의 남은 의무

현재 노드는 P4-S4C-SPECTRAL-EDGE-SUPPORT/SUBTHRESHOLD-SURVIVOR-RESOLUTION이다. 이 bounded work로 전체 노드를 완료 처리하지 않는다. 실제 gas path의 knot 사이 enclosure, 연속 source feedback, continuous spectral refinement, angular convergence, birth-time continuum, whole donor domain, full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, Li/Be 및 nuclear T1–T8을 모두 유지한다. 원래45-node 및26-node DAG는 byte-exact 사본으로 별도 보존한다.

## Primary references

- NIST DLMF, §3.5, quadrature 및 Gaussian rules: https://dlmf.nist.gov/3.5
- SciPy PchipInterpolator, C1 regularity와 second derivative jumps: https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html
- Verner et al. photoionization fit 자료 및 원 논문 연결: https://www.pa.uky.edu/~verner/photo.html

문헌의 일반 성질과 이번 실행의 NUMERICALLY_CHECKED 결과를 구분한다. 실제 Python/NumPy/SciPy 버전은 실행 receipt를 따른다.
