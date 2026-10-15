# REI Σ–π_ab: LRS Bianchi I의 Einstein–radiation–matter 연구 루프

2026-10-15 KST. 정확한 출발점은 rei_bianchi PR #129 commit fa20d75e344a28c833a47cbca82315ccbbdf6882. 과거 원본 AX08 이력, 현재 REI source/시나리오/저장 checkpoint/Rust 실행을 변경하지 않았다. 이번 독립 계산은 Σ 및 응력의 결합을 실제로 적분하는 source-defined **collisionless homogeneous Einstein pilot**이다. 원본 REI H/He의 동적 화학 및 stellar UVB를 포함한 full native science solver는 별개이다.

## 1. 정의, 부호 및 원래 REI 데이터와의 연계

계량 signature (-,+,+,+):

\[
ds^2=-c^2dt^2+a(t)^2[e^{-2b}(dx^2+dy^2)+e^{4b}dz^2],\quad s=\dot b.
\]

직교틀의 σᵢⱼ=diag(-s,-s,2s), σ²≡σ_ab σ^ab/2=3s². 사용자 지정 Σ≡|σ|/H=√3|s|/H를 기본 무차원 변수로 채택한다. Σ≥0만으로는 부호가 정해지지 않으므로 orientation=sgn(s)∈{-1,0,+1}을 별도 표시한다. 일부 문헌의 Σ_+=s/H 또는 σ/(√3H)와 normalization이 다르다. 이전 사용되었던 source의 q_ref=s_ref/H_FLRW,ref는 변경 불가능한 historical provenance일 뿐 새로운 물리 모델의 입력이나 출력명으로 쓰지 않는다. Stress-free source에 대한 compatibility map:

\[
\Sigma_{\mathrm{ref}}=\frac{\sqrt3|q_{\mathrm{legacy}}|}{\sqrt{1+q_{\mathrm{legacy}}^2}},\qquad
q_{\mathrm{legacy}}=\frac{\epsilon_s\Sigma_{\mathrm{ref}}}{\sqrt{3-\Sigma_{\mathrm{ref}}^2}}.
\]

이 식은 원래 source의 H²=H_FLRW²+s² 조건에서만 정확하다. 새 backreacting metric에서는 직접 H 및 s에서 Σ를 측정한다.

Stress tensor는 πᵢⱼ(A)=diag(-Π_A/3,-Π_A/3,2Π_A/3), Π_A=p_parallel(A)-p_perp(A), A∈{radiation,matter}. 따라서 σ_abπ^ab=2s(Π_r+Π_m). Einstein 제약과 전단의 source:

\[
H^2=\frac{8\pi G}{3c^2}(\varepsilon_{\mathrm{rest}}+u_m+\varepsilon_r)+\frac{\Lambda c^2}{3}+s^2,\qquad
\dot s+3Hs=\frac{8\pi G}{3c^2}(\Pi_r+\Pi_m).
\]

선택한 collisionless sector에서는 각각

\[
\dot\varepsilon_r+4H\varepsilon_r+2s\Pi_r=0,\quad
\dot u_m+5Hu_m+2s\Pi_m=0,\quad
\dot\varepsilon_{\mathrm{rest}}+3H\varepsilon_{\mathrm{rest}}=0.
\]

평균 H 방정식 독립 검증:

\[
\dot H=-\frac{4\pi G}{c^2}\left(\varepsilon_{\mathrm{rest}}+\frac43\varepsilon_r+\frac53u_m\right)-3s^2.
\]

코드는 c,G,k_B,m_p를 SI 단위로 유지하며 Π와 ε는 Pa=J/m³다. 시간 변수 η=ln(a/a_ref)를 적분하고 dt/dη=1/H를 **세 번째 동적 상태**로 적분하여 거대한 기존 timestamp 뺄셈을 피했다.

## 2. 실제 kinetic source, 모델의 closure 경계

Radiation: 초기에 등방인 massless effective Ω_r bath를 collisionless Killing momentum으로 수송한다. 초기 방향 μ_*에서 에너지 redshift factor

\[
R(\mu_*,b)=\sqrt{e^{2b}(1-\mu_*^2)+e^{-4b}\mu_*^2}.
\]

\[
\varepsilon_r=\varepsilon_{r,*}e^{-4\eta}\int_0^1R\,d\mu_*,
\quad p_{\parallel,r}=\varepsilon_{r,*}e^{-4\eta}
\int_0^1 \frac{e^{-4b}\mu_*^2}{R}\,d\mu_*,
\]
\[
p_{\perp,r}=\frac12\varepsilon_{r,*}e^{-4\eta}
\int_0^1 \frac{e^{2b}(1-\mu_*^2)}{R}\,d\mu_*,
\qquad\Pi_r=p_{\parallel,r}-p_{\perp,r}.
\]

이것은 단순한 유한 multipole 자의적 closure가 아니라 source Maxwell/Planck 초기 각도분포의 exact massless collisionless T_ab 모멘트다. Ω_r에는 원본 REI의 CMB+효과적 massless radiation 전체를 사용한다. 별도 ionizing stellar photon reservoir와의 energy double counting은 하지 않았으며, 그 contribution은 다음 단계에 남긴다. Wolfram 직접 적분의 작은 b 계수:

\[
\varepsilon_r/\varepsilon_{r,\mathrm{iso}}=1+\tfrac85b^2+O(b^3),
\quad p_{\parallel,r}/\varepsilon_{r,\mathrm{iso}}=\tfrac13-\tfrac{16}{15}b+O(b^2),
\quad p_{\perp,r}/\varepsilon_{r,\mathrm{iso}}=\tfrac13+\tfrac8{15}b+O(b^2),
\quad \Pi_r/\varepsilon_{r,\mathrm{iso}}=-\tfrac85b+O(b^2).
\]

Matter: 선택한 비상대론적 neutral H/He 및 잔류 전자 kinetic ensemble의 초기 pressure p_*=(n_H+n_He+n_e)k_BT_*에서

\[
p_{\perp,m}=p_*e^{-5\eta+2b},\quad
p_{\parallel,m}=p_*e^{-5\eta-4b},\quad
u_m=(2p_{\perp,m}+p_{\parallel,m})/2,\quad
\Pi_m=p_{\parallel,m}-p_{\perp,m}=-6p_*e^{-5\eta}b+O(b^2).
\]

고정 화학종 collisionless matter가 이번 기본 모델이고 isotropized_matter는 π_m=0의 명시적인 별도 control이다. 실제 중성 기체의 atomic collisions, Thomson drag, photoionization, heating/cooling, X-ray 및 nonlocal photon transport는 이 pilot에 없다. 따라서 full REI physical admission, posterior, primordial anisotropic recombination을 주장하지 않는다.

## 3. 실제 수치 결과

REI 시나리오 원본 SHA256=07aa11d2d3fd47d2ed95e9d9161f6205e4d9ba386c27ad43d2b298fcd86d1696. 원본 HyRec H+He FULL q=0 donor는 user-disabled candidate로 유지하며 source Git blob SHA1=1e3fdd5019f2a9a7d5ccd6a23e2f3a03faf74bd4, x_e(z20)=0.000210349192936, T_m(z20)=9.306042400380866 K. 원본 REI baseline은 x_e=.0002, T=8.098143045064857 K. 2 gas cases × 5 signed Σ instances × Einstein/prescribed 비교에 isotropized controls 추가: 실제 28개 독립 DOP853 이력, CSV 3,388행.

| donor, zbar4 | 초기 Σ_ref | orientation | stress-free 종료 Σ | π_r+π_m backreaction 종료 Σ |
|---|---:|---:|---:|---:|
| small | .0086601458 | + | .0009999514365 | .0009912902846 |
| small | .0086601458 | - | .0009999514365 | .0009912605458 |
| large | .0173196421 | + | .0019999018732 | .0019826095514 |
| large | .0173196421 | - | .0019999018732 | .0019824906007 |

큰 +분기 종료 ΔΣ/Σ_old=-.00864658514 (약 -0.865%). 같은 물리에서 Π_r=-4.133671066088808e-13 J/m³, Π_m=-6.559763156275732e-24 J/m³, 따라서 |Π_m/Π_r|=1.586909807625898e-11. Matter stress 계산은 생략하지 않았고 collisionless pressure tensor에서 직접 얻었다. 다만 이 비율을 다른 gas kinetic model로 일반화하지 않는다.

새 proper clock: 큰 +분기 종료 source-prescribed elapsed t=4.279464240897772e16 s, coupled elapsed t=4.279464144932797e16 s. 동일 zbar4에서 Δt=-959649752 s (상대 -2.24245e-8). 동일 proper-time 비교는 다른 estimand이며 여기서는 하지 않았다.

## 4. Native REI perturbative stress와의 독립 비교

원래 REI PR129에서 저장된 실제 312238-row radiation feedback에서, +small 사례의 **initially isotropic effective radiation**에 대한 perturbative Δ(s/H)=-5.00511315341987e-6; 실제 stellar ionizing photon contribution은 -6.293776580571164e-14. 이번 Einstein-integrated Σ 결과와 source-prescribed Σ 결과의 차이를 sign과 √3으로 정확히 변환하면 Δ(s/H)=-5.000518386820171e-6. 두 서로 다른 계산의 상대 차이는 0.00091801453, 즉 0.0918%. Source saved feedback JSON의 SHA256=4dcabe44002e34133fe56c6c56926040a67c711511a82c5e388f06b2e706c45b. 이 검증은 기존 native radiation transport의 perturbative diagnostic과 새 nonlinear geometry의 수치 일관성이고 **실제 native photon/gas solver를 stress-coupled geometry로 재실행한 parity가 아니다**.

## 5. 성능, 검증, 산출물

- Native source에서 기존의 isotropic_initial_radiation_moments를 호출하는 새 independent Rust example은 실제 release build 성공, 9개 b 노드 출력. 새 Python GL64 positive-half quadrature와의 수치 일치 tests PASS.
- 8192 b samples × GL64 angular integration: scalar median 0.087067889 s, memory-bounded NumPy batch 0.001970724 s, **44.18x faster**, 최대 scaled relative difference 3.4783e-12. 이것은 radiation moment만의 결과다.
- 28 standalone full IVP cases: serial wall 0.9860 s, 2-process pool wall 0.5071 s, **1.94x batch speedup**. 실제 endpoint Σ,b는 동일. Multiprocessing은 native subagent가 아니다.
- 변경 대상 Python scientific tests **18 PASS**, Rust standalone \Sigma 및 anisotropic-stress SI identity **3 PASS**, 기존 native Rust axbi_background release tests **6 PASS**. Raychaudhuri finite-difference 검증, Hamiltonian, radiation pressure trace, mass/energy contraction, 수송 에너지 대 b derivative, independent GL order 및 ODE time refinement, donor/provenance 부정 테스트를 통과했다.
- Source-coupled output: RESULTS.json, NATIVE_FEEDBACK_CROSSCHECK.json, SIGMA_PI_HISTORY.csv, SIGMA_PI_COMPARISONS.csv, NATIVE_RUST_RADIATION_ORACLE.csv, PNG science charts. 생산 REI 원본 branch와 checkpoint, legacy q_ref source-identity는 변경하지 않았다. local Codex 미사용, native subagent 도구 부재 NOT_RUN.

## 6. 다음 constructive step

현재 소스에 Π_total=Π_initial effective massless radiation+Π_ionizing+Π_matter를 제대로 결합하려면, REI native emission/opacity solver의 photon energy와 J2 (=P2 weighted angular energy)에서 Π_ion=nH_m3 J2_eV_per_H (1 eV in J)를 같은 atomic step과 ledger로 함께 업데이트해야 한다. 이 photon-momentum/energy source를 Einstein 식에 더하기 전에 double counting 금지 및 Compton gas exchange를 만족해야 한다. Matter는 고정 중성 H/He의 collisionless model을 실제 collision operator 또는 source-verified shear viscosity/relaxation closure로 승격하고, 열 생성 항 -σ_abπ^ab와 baryon/charge ledger를 포함해야 한다. 그 다음에만 별도 새 native scientific source/binary/checkout에서 Σ, orientation 두 입력과 원본 baseline을 fresh initial 상태에서 비교하고 numerical AX11 gate를 수행할 수 있다.

관련 1차 문헌: Heinzle & Uggla, Classical and Quantum Gravity 23 (2006) 3463-3489, https://arxiv.org/abs/gr-qc/0512031; 원본 REI 실제 데이터와 prior feedback은 PR129 https://github.com/cosmosapjw-quantum/rei_bianchi/pull/129; REC primordial donor는 PR94 https://github.com/cosmosapjw-quantum/rec_bianchi/pull/94.

**판정:** 정확한 계량과 가정 내에서 유도/국소 수치검증/국소구현 검증된 Einstein–collisionless-radiation/matter Σ/π pilot. REI stellar-photoionization–matter stress complete coupling: NOT_RUN. Observational admission: NOT_ISSUED.
