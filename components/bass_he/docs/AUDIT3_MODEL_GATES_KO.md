# AUDIT3 — DR8V surrogate stress, DR9A trajectory gate, DR9B exponent/channel audit

## DR8V surrogate adversarial validation

The local-cubic surrogate in u=rho^2 was challenged against exact geometry at 30 endpoint-near points (0.90, 0.95, 0.98, 0.99, 0.995, 0.999 of each branch support) and 70 new child nodes from the only refined GK7 interval. All 100 exact solves succeeded. Maximum endpoint-near relative Delta error was 7.1816e-6; maximum refinement-node error was 4.0069e-5 (S23). Both are below the runtime gate 2e-4. This is held-out numerical validation, not a global interpolation bound.

## DR9A trajectory-domain gate

Stolterfoht et al. (Phys. Rev. A 81, 052704, 2010) state that realistic classical internuclear trajectories are crucial for the low-energy rotational/isotope effect and that straight-line trajectories cannot reproduce that effect. Their head-on estimates at 100 eV/u are Rmin≈0.65, 0.40, 0.30 a0 for H, D, T.

For the inherited clean-room S_lsigma matching radius, the diagnostic equality Rmin=Rmatch occurs at approximately:
- l=1: H 111.43, D 68.57, T 51.43 eV/u;
- l=2: H 33.91, D 20.87, T 15.65 eV/u.

These are not physical validity thresholds because Rmatch is a clean-room matching convention. At 0.5 keV/u the source puts the system near the transition to radial dominance, so the trajectory-model gate remains open. At 5 keV/u straight-line motion is more plausible, but not independently validated. No production extension below 0.5 keV/u is authorized without a trajectory-aware model or benchmark.

## DR9B factor-of-two and upper-shell semantics

CPC 2023 prints Eq.(52) as p=exp(-Delta/v) for an elementary transition, while Eq.(55) calls exp(-2Delta/v) the Q-series single-pass transition probability. Eq.(56) defines Delta from the imaginary part of a complex action. If the same Delta normalization is used, an amplitude exp[i(S_R+i Delta)/v] has probability |A|^2=exp(-2Delta/v). Thus factor-2 has the standard amplitude-to-probability interpretation, while source normalization remains unresolved.

A fresh Nmax=3 shell-level comparison adds independent evidence. Against Appendix-A shell cross sections, factor-2 gives multiplicative RMS discrepancy about 1.41 across dominant n=2,3 shell points, versus 4.60 for factor-1. Across all six shell points including the tiny n=1 channel, the factors are about 1.98 and 64.0. Total capture model/source ratios are 0.554 and 1.219 for factor-2 at 0.5 and 5 keV/u, versus 5.947 and 2.996 for factor-1.

This strongly favors factor-2 as the theory/benchmark research lane, but does not authorize silently rewriting Eq.(52) or changing a production default. Appendix A also prints CX(n=3)=ionization at Nmax=3 at both test energies, and CORDIR shows an upper united-atom shell can correlate to a lower bound separated-atom shell. The upper-shell population is therefore a source truncation surrogate, not an independently additive physical ionization channel.

## Gates

- DR8V surrogate endpoint/refinement validation: PASS as held-out numerical evidence.
- DR9A trajectory adequacy at 0.5 keV/u: OPEN / transition-boundary regime.
- DR9A 5 keV/u: straight-line more plausible, not independently validated.
- DR9B exponent: factor-2 theory-and-author-benchmark favored; source normalization remains OPEN.
- Nmax upper-shell physical channel partition: OPEN.
- Physical production cross section / BASS CT2 promotion: CLOSED_NOT_STARTED.


## 5. DR9A Coulomb accessibility proxy

Source head-on Rmin을 repulsive Coulomb turning-point 식의 R0로만 사용하면, impact parameter b에 대해 rmin=(R0+sqrt(R0^2+4b^2))/2이고 주어진 matching radius Rcut에 도달할 수 있는 최대 b는 bmax^2=Rcut(Rcut-R0)이다. 따라서 straight-line disk pi Rcut^2 대비 접근 가능한 proxy area fraction은 max(0,1-R0/Rcut)이다. H, l=1 inherited Rcut에서는 이 fraction이 100 eV/u에서 0, 250 eV/u에서 0.554, 500 eV/u에서 0.777, 5 keV/u에서 0.978이다. 이것은 straight-line이 rotational window를 얼마나 과대평가할 수 있는지 보여주는 bracket이다. Stolterfoht 원문은 low-energy에서 Coulomb trajectory 자체도 rotational/isotope effect를 정확히 기술하지 못한다고 명시하므로 correction factor로 사용하지 않는다.

## 6. DR9B literature support for factor 2

Richter & Solov'ev, Phys. Rev. A 48, 432 (1993)은 같은 advanced-adiabatic/hidden-crossing 계열에서 branch-point transition probability를 P=exp(-2 Delta/v)로 쓰며, semiclassical action 형태 P(E,rho)=exp{-2 Im[S(E,rho)]}도 제시한다. 따라서 factor-2는 이제 단순 modulus-square derivation뿐 아니라 직접적인 선행 hidden-crossing 문헌 지지를 가진다. Appendix-A Nmax=3 shell benchmark도 factor-2를 강하게 선호한다. 다만 CPC 2023 Eq.(52)의 p=exp(-Delta/v) 표기가 어떤 내부 normalization/elementary-step convention을 뜻하는지는 여전히 해명되지 않았으므로 Eq.(52)를 오타로 확정하거나 production default를 바꾸지 않는다.


## 7. Observable-specific trajectory reconciliation

Nichols, Hanstorp & Cabrera-Trujillo, Eur. Phys. J. D 80, 34 (2026)은 coupled electron-nuclear LTDSE와 straight-line trajectory를 0.1--900 keV/u에서 직접 비교해 He2+ + H의 total electron-capture cross section에는 significant trajectory difference가 없다고 보고한다. 그러나 같은 연구는 low-energy 2s/2p state-resolved capture에서 straight-line이 각각 under/over-estimate하는 redistribution을 보이고, small impact parameter probability에서 trajectory difference가 가장 크다고 보고한다. Stopping/energy-loss 역시 trajectory sensitive하다.

따라서 Stolterfoht 2010의 저에너지 isotope/rotational trajectory sensitivity와 2026 total-capture robustness는 서로 배타적이지 않다. 현재 BASS_HE observable은 total 하나가 아니라 indexed-state distribution을 적분하므로 state-resolved trajectory gate는 OPEN으로 유지한다. 반면 total H-target capture에 대해서는 straight-line model을 자동 FAIL로 분류하지 않고 recent coupled-trajectory evidence에 의해 partially relaxed한다.
