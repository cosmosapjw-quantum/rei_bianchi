# HERE_RUX03_MOVING_GAS_SOURCE_05 — scientific contract

THEORY R1–R10; physmath-research-loop 1.0.0. Date: 2026-10-13 KST.
Parent: HERE_RUX03_COVARIANT_EXCHANGE_04, BASS_HE PR32 commit
`ca85cfc7353da190613f7fb37a6e0ffed9b51913`.

## Objective and selected construction

Construct the finite common-gas source substep left open by THEORY04. A fixed
local Eulerian tetrad supplies one time coordinate and one fixed spatial
volume. Lab photon energies/directions remain fixed during this source
substep. Absorption, atomic species changes, gas energy/momentum and Case A
escape use one candidate endpoint gas state. Photon backward Euler elimination
and gas primitive recovery turn this into a seven-variable implicit stage.

The scientific completion target is a derived finite map, exact source
balances, its admissible primitive domain, local physical branch existence,
and explicit zero-velocity/paired and one-beam constructions, with actual
Wolfram and xAct checks and independent review. The inherited geometry/work
substep remains separately owned by THEORY04.

## Definitions, normalization and domain

- Signature (-,+,+,+), physical constants c, hbar and k_B retained.
- Eulerian observer n.n=-1; gas u=gamma(n+beta), n.beta=0, beta²<1.
- D=gamma n_H is the conserved Eulerian H-nucleus number density.
- Fractions zeta=(x,f a,f b), with 0<=x<=1, zeta_2,zeta_3>=0 and
  zeta_2+zeta_3<=f. Electron count per H is x+f a+2f b.
- B=chi_0 x+f chi_1 a+f(chi_1+chi_2)b in eV per H. w is thermal eV per H.
  r=m_ref c²+epsilon_eV B>0, rho=n_H(r+epsilon_eV w),
  p=(2/3)n_H epsilon_eV w; Gamma=5/3.
- Gas conservative variables are Eulerian energy density E and energy-scaled
  momentum density M=c times physical momentum density:
  E=(rho+p)gamma²-p, M=(rho+p)gamma² beta. Their densities all use the fixed
  Eulerian volume. Their defining energy current is -T_g.n.
- N_q is the photon number density per fixed Eulerian volume. An actual cell
  count is V N_q for the same constant V. E_q denotes lab photon energy in eV;
  mathcal E_q=epsilon_eV E_q=hbar omega_q denotes physical energy.
- Direction-resolved photon k_q=n+e_q is null, n.e_q=0, e_q²=1.
  Doppler delta_q=-u.k_q=gamma(1-beta.e_q)>0.
- Atomic inputs are gas-frame energy E'_q=delta_q E_q, n_H=D/gamma,
  electron density, fractions and T=2 epsilon_eV w/[3 k_B(1+f+e)].
- Retain the existing warm FT03 and primary provider: T in [30000,110000] K,
  gas-frame E'_q in [0,50000] eV, CI/RR/two DR/primary absorption; CR/RCT/HH off.
  The local C1 branch theorem uses a strict warm/energy interior and a
  neighborhood avoiding the provider's piecewise energy cutoffs. General
  finite candidate admissibility is checked against the full stated domain.
- Escape is comoving-isotropic and uses exactly the inherited RR/DR binding
  plus captured-kinetic power. Its lab energy/momentum increments are
  h gamma Q'_esc and h gamma Q'_esc beta.
- h is the Eulerian time step. Proper event density per four-volume R' gives
  an Eulerian event increment h R'. Species per-H updates divide by D; the
  equivalent gas-clock step at a common endpoint is h/gamma.
- Full directional nodes support arbitrary beta. Existing azimuth-averaged
  rings retain their one-dimensional form for beta along the symmetry axis;
  transverse velocity uses resolved azimuth or the corresponding positive
  angular integral.

## Claims to derive and review

| ID | Target | Required evidence |
|---|---|---|
| M01 | Doppler beam/current map and invariant absorption-event normalization | explicit Lorentz contractions and event-count argument; xAct |
| M02 | Common-stage photon/species/gas/escape map with exact finite energy and momentum balances | algebraic elimination and shared event increments |
| M03 | Unique gamma-law primitive recovery with positive thermal energy iff E>sqrt((D r)²+|M|²) | monotone scalar proof, boundary and stable evaluation |
| M04 | Exact endpoint thermal identity including finite velocity/pressure correction | tensor projection, constitutive substitution, continuous limit |
| M05 | Local unique physical endpoint branch for sufficiently small h in a smooth strict interior | positive primitive Jacobian and implicit function theorem |
| M06 | Positive one-beam and rest-paired constructions and parent scalar limit | explicit family, binding budget and warm-domain argument |
| M07 | Computational contract and angular/domain adapters following the derived map | source mapping, units, root/domain residuals and traceable examples |

The independent reviewer receives the actual candidate and raw execution
results and owns the final scoped adoption decision. Authors do not write
their own independent decision.

## Evidence reuse and verification stop

Reuse THEORY04's accepted four-force, perfect-fluid projection, binding and
escape ownership, and its 45 final checks under their existing assumptions.
Reuse PRIMARY_THEORY_03's prior event/provider identities and 47 checks. Do
not rerun unchanged groups or add them to this unit's new execution count.
The selected receiver is PR114 `a5c958c414dea41216b445c05f58df837f05cacb`;
the source task verifies current identity and only the affected normalization
and state-ownership connections.

Actual new scientific execution is light Wolfram/xAct algebra. Native builds,
chemical RHS and ODE/history campaigns remain in their existing CODING lanes.
Stop new checks after the candidate's concrete algebra/domain risks and
independent findings are resolved. Preserve environment or derivation
failures by their actual class, input and output.

## Research and delivery ownership

Root: Doppler/events, common-stage construction, finite thermal identity,
local branch proof, xAct execution and synthesis.
Primitive author: global inverse and exact constructions.
Independent reviewer: primary literature comparison and final claim review.
Source/publication task: current source identities and later isolated draft PR.

The original PRIMARY_PROVIDER_03 coding successor and owner DAG remain in
place. The next mathematical obligation is selected from the actual remaining
coupling/continuation questions after this unit's decision. Authorized delivery
uses an isolated draft PR, create-only Drive/Dropbox copies and final report,
coding contract, complete evidence archive and delivery record.
