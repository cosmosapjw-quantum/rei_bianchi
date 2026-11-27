# A2 결과: 두 극한의 정확한 계수와 completed connection

A2에서 exact R10R bright coupling의 작은 R·큰 R leading coefficient와 잔차를 직접 유도했다. 대상은 하나의 전자, spinless, 비상대론적 point-Coulomb H/He, charge-center 원점, lowest m=0 및 lowest real bright |m|=1 상태다. 양의 meridional phase를 유지한다. 이 보고서의 최종 admission은 `review/A2_INDEPENDENT_REVIEW.json` 및 `RESULT.json`에 연결된다.

x=R/a_A, a_A=ℏ²/(m_eκ), κ=e²/(4πε₀)로 두면

\[
\langle g_R,L_y^O b_R\rangle
=-i\hbar\frac{4\sqrt2}{15}x^3+O(\hbar x^{7/2})\quad(x\downarrow0),
\]
\[
\langle g_R,L_y^O b_R\rangle
=-i\hbar\frac{32\sqrt2}{243}x+O(\hbar x^{-2})\quad(x\to\infty).
\]

작은 R의 첫 항은 핵 근처를 포함하는 정확한 shifted-Coulomb 적분에서 나온다. 외부 dipole 소거와 quadrupole/octupole 선택규칙만으로는 이 cubic 항을 얻지 못한다. Fourier H⁻² estimate, H² algebra, 고립 sector resolvent와 두 remainder를 사용하여 원자 comparison integral을 exact molecular theorem으로 연결했다. 단순 1차 섭동계수의 추측으로 남겨 두지 않았다.

큰 R에서는 sector gap, 명시적인 atomic polarization correction, reduced-resolvent quadrupole correction 및 H¹–Hardy torque bound를 사용했다. He-centered intrinsic coupling은 +iℏ(128√2/729)x⁻²+O(ℏx⁻³)로 감소한다. Charge-center의 선형항은 origin lever와 연결되며, 전체 ETF generator에서는 translation·rotation·boost를 함께 변환해야 한다.

선택한 exact B-centered ETF pair entry는 e^{iΔγ}[m_e a_{B,x}d_{gb}−Ω_y L^B_{gb}]다. 직선 등속 경로의 큰 R에서는 이 entry가 O(R⁻⁴)다. 작은 R에서는 같은 B-ETF의 회전항이 O(ΩR)이고, O-centered ETF의 bare 회전항은 O(ΩR³)다. 서로 다른 spatial boost를 포함하므로 power가 달라도 모순이 아니다. 전체 physical capture amplitude에 universal power나 nonzero를 부여하지 않았다.

R10R strict positivity와 두 극한, strong form continuity를 결합하면 x³/(1+x²)에 대한 전 R 양의 two-sided comparison bound가 존재한다. 상수는 계산하지 않았으며 이 weight를 fitted/interpolated coupling model로 채택하지 않는다. He n=2/H1s rank-5 cluster, 중심별 1/R detuning, rank-4 shell의 leading dipole·quadrupole block도 정리했다. Leading Stark eigenvectors와 exact finite-R eigenvectors를 구분한다.

Full P⊕Q의 off-diagonal tail은 A1b 경로 조건에서 O(t⁻²), exact memory kernel norm은 양 끝 residual bound의 곱으로 제어된다. Q_Q generator의 norm 감쇠, Q amplitude의 소멸, 6채널의 정확도 또는 전체 산란 완비성은 결론내리지 않았다.

실제로 새로 수행한 계산은 **Wolfram exact CAS 1회**다. 출력 8항목에서 cubic coefficient, shifted integral series, 두 polarization ODE residual 0, n2 projected constants 및 intrinsic coefficient를 확인했다. Functional-analytic proof와 CAS의 역할을 구분했고 독립 reviewer가 별도로 수식·domain·부호·gauge·claim 범위를 심사했다. Python 과학 suite나 기존 CAS/tests는 재실행하지 않았다.

기존 P06/P23/P24를 선택 열람했고 GK1961 원문 1편을 새로 확보해 private archive에 포함했다. 문헌은 UA/SA 구조와 origin compensation을 지지하지만 새 Ly 계수·norm remainder의 authority는 이번 직접 증명이다. B1의 1,131개 native cells·13행 matrix는 바꾸지 않았다.

Finite-R physical eigensolve, coupling grid, collision propagation, impact integration, channel/continuum convergence, benchmark fitting, Eq55는 모두 NOT_RUN이다. 전체 프로그램은 미완료다. 다음 단일 node는 **C1 — two-center electronic solver architecture**이며 세부 계약은 `NEXT_HANDOFF_KO.md`에 있다.

CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.

전체 유도는 `A2_ASYMPTOTIC_DERIVATION_KO.md`와 두 author notes에, 실제 입력·출력·identity는 manifests와 evidence에 있다. 게시 commit/tree 및 Drive/Dropbox 저장 확인은 별도 delivery receipt가 소유한다. 업로드와 raw restore 검증은 구분한다.
