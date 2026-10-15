# REI × BASS: 초기 shear와 초기 비등방응력 π_ab의 상쇄와 남는 metric 기억

2026-10-15 KST. 실제 사용자 Ubuntu에서 새로운 이론·수치·Rust 연구 코드를 직접 실행했다. 기존 REI native short-proper-clock C9 PR127은 이미 완료된 출처로 사용하며 재구현하지 않았다. 연구 기반은 최신 REI PR140 HEAD b1cba753083ad83049c23ff538834564b49b7b6e 및 BASS PR160 original finite-mass hierarchy SHA 1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790. 원본 AX08 owner checkout, checkpoints, production Rust 및 다른 개발 브랜치는 변경하지 않았다. 별도 Codex 미사용, native AI subagents NOT_RUN (host에 dispatch 도구 없음).

## 1. 물리 규약·최종 배경해의 해석

비틸트 LRS Bianchi I, signature (-,+,+,+):
ds²=-c²dt²+a² exp(-2b)(dx²+dy²)+a² exp(4b)dz², s=db/dt.
sigma^i_j=diag(-s,-s,2s), pi^i_j=diag(-pi_s,-pi_s,2pi_s),
pi_s=(p_parallel-p_perp)/3 (Pa 또는 J/m³).
사용자의 비음수 전단 스칼라 Sigma=sqrt(sigma_ab sigma^ab/2)/H=sqrt(3)*abs(s)/H이며 별도 orientation=sign(s)를 반드시 보존한다. 원래 입력 q_ref는 source 내부 호환 signed 초기 전단이며 Sigma 자체가 아니다. 해당 source-bounded 모델의 Einstein shear와 Hamiltonian은 다음과 같다:

ds/dt+3Hs=(8 pi G/c²)*(pi_gamma+pi_nu+pi_massive),
H²=H0²*(Omega_dust/a³+normalized_massive_energy+normalized_gamma+normalized_nu+OmegaLambda)+s².

원래 massless gamma/nu는 별개 양의 P2 각분포 W=1+kappa P2, 충돌 없는 ν와 gamma-only 불편광 Thomson (E/B 편광 OFF). 원래 BASS160 FD 유질량 궤적은 velocity-index i=0..2 및 l=0,2를 실제 적분하고 누락된 상위 i/l4는 진짜 Killing/Vlasov source로 공급한다. f_massive=0.1의 에너지는 기존 Omega_m의 비바리온 dust에서 떼어내고 다시 더하지 않는다. 초기 A_massive=+0.5 또는 -0.5와 mass/Tref=30,300은 가정한 물리적 양의 분포로 특정 관측 neutrino mass와 동일시하지 않는다.

정확한 source-integral Green identity:
a_end³*s_end - a_ref³*s_ref
  = (8 pi G/c²) integral_[ln(a_ref), ln(a_end)] a³*pi_s/H dln(a).
이로부터 마지막 시점의 signed s/H=0은 초기 s_ref와 이전 pi_s source의 유한 시간 work가 상쇄된다는 암시적 (nonlinear) shooting 조건이다. Photon number and energy source-normalized individual gamma/nu/massive positive input constraints preserved. Wolfram Engine15.0.0 실제 테스트는 sigma²/2=3s², sigma_ab*pi^ab=6s*pi_s, Green derivative, P2 normalization, tracefree tensors와 q→Sigma 7개 원식을 정확히 0으로 검산했다.

## 2. 구성적 수치 결과: 초기 π와 초기 s의 독립 초기조건

초기 gamma/nu 사중극자 kappa_gamma=kappa_nu=0.2, mean redshift20→4. 종말 Sigma(절댓값)가 아닌 signed s/H=0을 목표로 brentq로 풀었다. 가장 중요한 Thomson OFF ROOT 및 metric b memory:

| 초기 positive kinetic 분포 | root q_ref | b(zbar=4) |
|---|---:|---:|
| gamma+nu only | -0.000515004627091 | -0.000218871936340 |
| gamma+nu, massive A=+.5, m/T=30 | -0.000661027799344 | -0.000271697052423 |
| gamma+nu, massive A=-.5, m/T=30 | -0.000370160463593 | -0.000166632622648 |
| massive only A=+.5 | -0.000145367861231 | -0.000052502603536 |
| massive only A=-.5 | +0.000145345491736 | +0.000052493081141 |
| gamma+nu with colder massive m/T=300 | -0.000516482820364 | -0.000219405420488 |
| gamma only | -0.000304704267337 | -0.000129494855271 |
| nu only | -0.000210237553154 | -0.000089347423986 |

주요 gamma+nu,massive +.5 사례에서 Sigma_ref=1.144933483535085e-3, 실제 마지막 signed s/H≈1.07e-14이나 b=-2.7169705242e-4. Source-free Killing photon redshift transverse/longitudinal 차의 로그값은 -3*b=8.15091157267e-4로, 방향 간 상대 에너지 인자 exp(-3b)=1.0008154234343372. **순간 전단이 거의 없어도 축의 누적 비등방 metric/광자 수송 기억은 없어지지 않는다**는 구성적 예이다. 이는 지정한 균일 초기 분포 모델의 local degenerate source family이지, 관측 검출이나 문헌 최초의 정리가 아니다.

초기 s=0, 초기 pi=0 음성 대조는 마지막 s,b=0. 초기 s=0이고 pi≠0이면 소스에 의해 실제 shear가 발생한다. 주요 A=+.5의 초기 pi_s,γ=1.08255927695e-10 Pa, pi_s,ν=7.46970670211e-11 Pa, pi_s,m=1.04723022668e-10 Pa. Green identity 좌우는 source-evolved 241 state Simpson에서도 상대 defect <=1e-9로 일치했다.

## 3. 실제 AX08 H/He electron Thomson 공급의 영향과 불확실성

PR137 source-authenticated 원래 ZERO H/He electron history 312238 rows, SHA256 4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f, positive 8193-knot C2 interpolant를 gamma Thomson에만 공급하고 ν와 massive에는 직접 scattering을 넣지 않았다. 재해계산된 종말 shear cancellation root는 주요 massive +.5 사례에서 -0.000661027799344 → -0.000658068520099 (shift +2.959279245e-6), gamma+nu only에서 -0.000515004627091 → -0.000512056209909. Gamma-only κ seed에 대해 root shift ≈2.94e-6, massive-only shift ≈5.55e-9. 이는 소스 조건부 **one-way Thomson 효과**이고, 바뀐 Einstein metric 하에서 동일 원래 H/He chemistry/ionization history를 자기일관적으로 재적분한 것이 아니다. 전자원 interpolant 자체의 보고된 최대 상대오차 1.9755e-4도 별도 source uncertainty로 보존했다.

## 4. 실행/동일한 이론 식/수치 정밀도

PR140 네 소스 massive_radial.py, species_hierarchy.py, lrs_boltzmann.py, run_hierarchy.py를 SHA256 byte-lock한 뒤 additive new module initial_cancellation.py로 실제 계산했다. 8 case roots + 8 seeded controls, Thomson OFF vs original HHe ne one-way ON 모두 실제 적분, source signed parity, positive pressure cone and gamma/nu photon number invariants verified. Test suite newly **30 PASS**; inherited PR140 direct massive-source parity **13 PASS**. Initial Python test incorrectly referenced nested result key (schema mismatch only), corrected without modifying source, tolerance or numeric result; 30/30 green evidence preserved.

At cancellation root source hierarchy gravity_owner vs truly independent original exact Killing/Vlasov gravity_owner (same mass, angular positive distribution, no Thomson) gave b endpoint |difference|≈7.32e-16, signed s/H difference <7e-15 and pi_massive difference≈1.73e-22 Pa. Source-grid/timestep check nominal 64 radial×24 mu, photon L8,i2 vs high 128×64,L12,i4 confirmed endpoint s/H differences ~2e-15 for zero Thomson and ~1.7e-13 with original HHe electron. **These are local empirical convergence checks, not global AX11/observational error bounds.**

Original BASS160 source vectorized J0/J2/J4 on 768 matched FD source states: fair scalar once-per-all-moments median 0.0660465s; chunk16 ~2.31x faster with tracemalloc peak2.878MB; chunk32 ~2.33x with peak5.647MB. Chunk16 is a sensible practical compromise because throughput differs ~1% while traced memory is ~half. Peak is not total RSS. Independent eight q-shooting solves: serial median4.5618s, 2 Python processes2.2736s, 4 processes1.2733s, measured 4process **3.58x** faster with identical physical root/b outputs. Processes are not native AI subagents and are NOT native H/He production solver performance claims.

## 5. REI physical supplier bridge created and exercised

export_rei_background.py actually integrated **24 physical case histories×161 sample events=3864 rows** into REI_SIGMA_PI_BACKGROUND_3864.csv:
  8 stress-only initial Sigma=0;
  8 independent signed q cancellation without Thomson;
  8 independent signed q cancellation with actual saved original HHe electron Thomson.
Each row contains proper_elapsed_s in SI seconds, mean a/zbar, H,Hperp/Hparallel,s,b, user Sigma_abs, orientation, q compatibility input, separate physical pi_gamma/nu/massive in Pa, energy sectors, fixed ne donor (not evolved under changed geometry), conserved photon/nu number and Hamiltonian residual. Original source/case/unit binding and table SHA in REI_SIGMA_PI_SUPPLIER_CONTRACT.json.

rust_pi_supplier_consumer.rs is a **real compiled Rust stdlib-only input validator**, not the native production scientific integrator. It read all 3864 rows and checked Einstein Hamiltonian, Sigma vs signed s/H, source energy, directional H, physical pressure tensor amplitude, number monopoles, proper-time monotonicity and endpoint cancellation plus nonzero b. Same binary accepted original table and rejected three altered copies with exit3: H×1.05 (Sigma firewall), dust energy×1.05 (Einstein constraint), total pi×2 (pressure source sum); source CSV byte digest unchanged. First positive/negative harness had wrongly expected tampered H to fail at Hamiltonian, but the strict Sigma check rejected it earlier. Test expectations were repaired and a separate dust-mutation introduced to reach Hamiltonian; **no physics gate weakened**.

**Strong integration boundary:** Old production REI AxbiBackground and its short-time GL4 driver PR127 assume stress-free s∝a^-3. With nonzero pi_ab the correct background is the actively integrated Einstein–Boltzmann–Vlasov ODE, so the new CSV is **opt-in only** and old AX08 checkpoints cannot be resumed with this new source version. A native Einstein-backed background interface, retested chemistry and ionizing radiation RT in the changed metric, true H/He photon stress and source-unique checkpoint identity are needed before native science admission. No automatic merge into REI main or reproduction of final physical EoR ion abundances is claimed.

Source-oriented next work: implement/validate production-matched stress-coupled native provider, use original Case-A H/He and realistic photon emission to recompute n_e rather than frozen q0 history; integrate gamma-only Thomson backreaction, massive momentum l>2 and radial hierarchy without the external exact moment oracle; separate observational likelihood and AX11 science gates. General homogeneous Bianchi I exact signed stress and positive angular source are preserved for future extensions.
