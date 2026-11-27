# A2 독립 수학·물리 검토

판정은 **`SMALL_LARGE_R_ASYMPTOTICS_CLOSED`**다. 한 전자 spinless 비상대론적 H–He clamped point-Coulomb Hamiltonian, R10R의 양의 meridional 위상, exact lowest σ와 lowest bright |m|=1 pair에 한정하여 두 끝점의 leading coefficient와 remainder가 유도되어 있다. 명시된 frame/ETF 기저에서의 연결, 퇴화 cluster 및 full P⊕Q tail 구조도 이 범위에서 정합적이다. 다음 단일 의존성은 **C1 electronic solver architecture**이며 C1 자체는 NOT_RUN이다.

검토자는 두 저자 노트와 root 본문을 독립적으로 읽고 적분·부호·계수·resolvent 및 domain 논증을 점검했다. 검토 중 proof threshold와 필요한 오차 추정을 저자에게 전달했지만, 저자 파일이나 root 유도를 작성·편집하지 않았다. 새 계산 실행, 기존 시험 재실행, molecular eigensolve는 하지 않았다. 제공된 새 Wolfram 입력과 실제 raw response를 읽었으며 CAS가 functional analysis를 증명했다고 간주하지 않는다.

최종 검토 본문은 `A2_ASYMPTOTIC_DERIVATION_KO.md`, 16,317 bytes, SHA256 `b3c4175f429b02a3459540bdd7b7b66ed424bcb4f3af2f31f4faba4370432cd4`다. 두 저자 노트·CAS·계약·gate의 정확한 identity는 동반 JSON에 기록한다. R10R의 이미 채택된 finite-R nonzero theorem과 A1b의 exact P⊕Q formulation은 입력 의존성으로 사용했다. 문헌 검토 노트는 읽었으나, 이 검토자가 원문 PDF를 다시 열람했다고 주장하지 않는다.

## 1. 작은 R: 원자 계수와 exact molecular remainder의 연결

Charge-center dipole cancellation은 외부 multipole의 첫 항을 없애지만, 핵 주변 r=O(R)의 기여까지 없애지는 않는다. 정확한 UA transition-density convolution의 odd expansion은

\[
F(d)=\frac{4\pi d}{3\lambda^2}-\frac{2\pi d^3}{5}
+\frac{2\pi\lambda}{9}d|d|^3+O(|d|^5)
\]

이며, \(\sum_C\kappa_C z_C^3=-2\kappa R^3/9\)를 대입한 계수와 부호를 독립적으로 확인했다. 이 원자 적분만으로 분자 결과를 선언할 수 없다는 초기 경계를 최종 저자 증명은 지킨다.

S.10–28의 추가 논증이 핵심이다. Translated Coulomb의 균일 H² graph bound, charge-center Fourier cancellation에 의한 \(\|W_R\|_{H^{-2}}=O(R^2)\), \(\|L_yW_R\|_{H^{-2}}=O(\hbar R^2)\), 3차원 H² multiplication 및 고립된 sector resolvent를 결합하여 두 exact eigenvector의 L² 오차가 O(R²)임을 얻는다. L이 unbounded라는 문제는 별도로 \((H_R-E_g)L_yg_R=-(L_yW_R)g_R\)라는 분포식과 reduced resolvent를 써서 해결한다. \(L_yg_R\in D(H_R)\)를 가정하지 않으며, 각 bound state의 decay로 L² 존재를 확보한 뒤 차수를 추정한다.

\(\|W_Rp_{z0}\|_2=O(R^{3/2})\)의 scaling integral은 핵 근처와 무한원에서 모두 유한하다. 따라서 projection identity의 molecular 오차는 O(R^{7/2}), \(\langle L_yg_R,b_R-b_0\rangle\)는 O(ℏR⁴)다. 두 항 모두 leading R³보다 작다. 이로써

\[
\mathcal L^O_{gb}=-i\hbar\frac{4\sqrt2}{15}(R/a_A)^3
+O\!\left(\hbar(R/a_A)^{7/2}\right)
\]

를 exact molecular pair에 대해 승인한다. 최적 remainder나 로그항의 부재는 승인 대상이 아니다. n=2 full-shell 퇴화를 개별 영분모로 나누지 않았고, 필요한 분모는 ground-to-n=2 gap 또는 고립된 fixed bright sector의 resolvent다.

## 2. 큰 R: localization, quasimode와 singular torque

고정 m sector에서 IMS partition과 min–max로 target의 유일성과 양의 spectral gap을 확보하는 논리는 타당하다. H1s–He(n=2)의 full-space 에너지 일치는 bright |m|=1의 작은 분모를 만들지 않는다. 서로 다른 질문인 full near-resonant cluster는 별도 rank-5 projector로 다룬다.

L5–L11의 두 dipole-polarization 함수에 직접 미분을 적용해 forcing의 계수와 부호를 확인했다. Quadrupole reduced-resolvent correction 후에는 원자 영역 Taylor remainder와 먼 핵의 Coulomb singularity를 분리하여 O(R⁻⁴) quasimode residual을 얻는다. Sector gap과 Coulomb form coercivity로 H¹ 오차를 같은 차수로 올린 뒤, Hardy bilinear bound로 singular torque를 추정하므로 검증되지 않은 weighted L-graph convergence를 사용하지 않는다.

z-parity에 의한 T_B의 R⁻² 보정 소거와 T_A의 leading dipole, gap의 monopole 소거를 확인했다. 최종 계수는

\[
\mathcal L^O_{gb}=-i\hbar\frac{32\sqrt2}{243}(R/a_A)
+O\!\left(\hbar(a_A/R)^2\right),\qquad
\mathcal L^B_{gb}=+i\hbar\frac{128\sqrt2}{729}(a_A/R)^2
+O\!\left(\hbar(a_A/R)^3\right)
\]

다. Charge-center 전체 R⁻² correction과 intrinsic B-centered coefficient를 동일시하지 않는다. Momentum은 H¹ 오차로 먼저 제어하고 exact commutator로 dipole을 구하므로, unbounded position expectation을 H¹ 수렴만으로 추정하는 오류도 없다.

## 3. 연결·projector·uniform bound의 정확한 범위

명시한 B-centered spatial ETF에서

\[
K^{B\mathrm{-ETF}}_{gb}=e^{i\Delta\gamma}
\left(m a_{B,x}^{\rm body}d_{gb}-\Omega_y\mathcal L^B_{gb}\right)
\]

는 moving/rotating orbital에 대한 product rule과 일치한다. 고정 body axes의 radial derivative는 m sector를 보존하여 이 특정 pair에서 0이다. Translation·boost·rotation을 함께 처리하면 charge-center lever가 정확히 상쇄된다. Small-R B-ETF의 O(ΩR)와 O-ETF의 O(ΩR³)는 서로 다른 spatial unitary 기저의 entry이며 모순이 아니다. 가속항, scalar time-gauge 및 full-space completion이 명시돼 있어 이를 보편적인 2-state transition law로 읽지 않는다. 1/R phase를 제거할 때 생기는 diagonal −κ_other/R의 부호도 맞다.

Root의 global comparison bound는 R10R의 strict sign, H¹ state continuity, uniform Hardy bilinear bound와 dense smooth approximation, 두 양의 endpoint ratio에서 얻는 비구성적 존재 정리다. Translated singular kernel의 operator-norm continuity나 계산된 c_±를 가정하지 않는다. Comparison weight는 coupling의 보간식 또는 수치 입력으로 승인되지 않는다.

Full P⊕Q tail의 K_PP, K_PQ, K_QP는 선언된 선형 탈출·bounded velocity·O(t⁻²) acceleration 조건에서 O(t⁻²)다. Unitary U_Q를 사이에 둔 memory-kernel norm bound는 두 bounded block의 곱에서 따르며 energy² 차원도 맞다. Unbounded K_QQ의 감쇠, Q amplitude의 소거, 6채널 정확도 또는 전체 산란 완비성은 따라오지 않으며 본문도 주장하지 않는다.

## 4. 수정 확인과 실제 검산 증거

초기 본문과 large-R 노트는 (2s±2p_z)/√2를 가리키는 문장이 exact finite-R eigenvector로 오독될 수 있었다. 요청한 정밀화가 반영되어, 최종본은 이를 **leading R⁻² projected dipole block의 eigenvectors**로 한정하고 R⁻³ 이상 보정을 명시한다. 두 level의 leading shifts ±3κ_Aa_B/R²와 separation 6κ_Aa_B/R²도 구분했다. 최종 식을 바꾸어야 하는 미해결 오류는 찾지 못했다.

새 Wolfram raw response는 isError=false이며 shifted-Coulomb series, small-R coefficient 4√2/15, 두 polarization residual 0, n=2 dipole −3a_B, quadrupole 24a_B²와 −12a_B², intrinsic coefficient 1024√2/729를 반환했다. 마지막 값은 αa_B²/R²라는 원래 normalization으로 읽으면 본문의 128√2/729와 일치한다. 이는 정확한 대수/적분 검산 1회의 증거이고 functional bounds의 자동 증명이나 물리 계산 결과가 아니다. 검토자 재실행은 0회다.

`scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`, `production_default_change=NOT_AUTHORIZED`를 유지한다. C1 architecture를 다음 연구로 열 수 있지만 finite-R solver·coupling grid·collision propagation·benchmark fitting은 이번에 실행하지 않았다. 본 독립 admission은 A2의 지정된 이론 범위만 닫는다.
