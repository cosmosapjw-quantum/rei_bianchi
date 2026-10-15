# AX08 collisionless phase-volume certificate + signed continuation, 2026-10-15

## Verified authority and owner isolation

Original owner root: `/home/cosmosapjw/Dropbox/bianchi/rei_bianchi`. Active development is in an isolated worktree on branch `research/ax08-direct-chat-20261015`, seeded from the PR #118 head `a6eba8d2dff6db0d0c0ac96352ece7032399525e`. The owner's canonical tracked HEAD has advanced independently due to SOURCE07 C8 research; this phase-volume test is additive and does not overwrite it. All AX07/AX08 physical inputs, binary, source-model/Case-A/atomic cross-sections, checkpoint, and archived output remain unchanged.

The current owner `SHEAR_MINUS_RESOURCE_CONTINUATION_001` has **one actual observed scientific launch** using the already frozen binding `ab08422299b2810cf96f991dbeac1a9d17a8d796e7733cfaceb2ba49387d6aa2` and Rust science binary `4243c744af3f3237ad0ca570b14fad8db4344f33be8fc29d8da9cfda8e811c74`. Preparation/controlled release and PID evidence are privately preserved at `driver/full/minus_continuation_001/launch_001/`, with no automatic retry. Public branch includes the earlier launcher and its four PASS tests, but not private NCP host, release file, or full signed binding payload. An independently implemented mechanical AST/binding verification passed locally; distinct-model scientific reviewer was NOT_RUN. **Do not promote release permission to scientific admission.**

At the first observed progress checkpoint, `accepted=202080`, `a=0.0893152132003713`. At a later read-back, `accepted=208140` and `a=0.0910227371373424`, demonstrating physical progression beyond the original 200,000-step stop. This is ongoing on local CPU0; completion to zbar4, terminal exit and next half-minus start are NOT asserted.

## Exact independent theory

Metric signature \((-+++)\), gas normal comoving, \(c\) explicit:

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,\qquad b(a_{\rm ref})=0,\quad \dot b=s.
\]

For an initial normal-tetrad direction \(\mu_*\) and a fixed covariant wavevector, define

\[
S(\mu_*,b)=(1-\mu_*^2)e^{2b}+\mu_*^2e^{-4b},\qquad
\frac{E}{E_{\rm ref}}=\frac{a_{\rm ref}}a\sqrt S,\qquad
J_\Omega=\frac{d\Omega_{\rm local}}{d\Omega_*}=S^{-3/2}.
\]

This is consistent with the production `CharacteristicRay::pullback` and `solid_angle_jacobian`. Photon phase-space volume and free-streaming number satisfy the **exact identity**

\[
\frac12\int_{-1}^{1}J_\Omega\,d\mu_*=1
\]

because \(S=A+C\mu_*^2,\ A=e^{2b},\ A+C=e^{-4b}\), and

\[
\int_0^1(A+C\mu^2)^{-3/2}\,d\mu
=\left[\frac{\mu}{A\sqrt{A+C\mu^2}}\right]_0^1
=\frac1{A\sqrt{A+C}}=1.
\]

The inverse current-sky representation is \(D(\mu,b)=(1-\mu^2)e^{-2b}+\mu^2e^{4b}\); the analogous integral of \(D^{-3/2}\) also equals one. These are two coordinate expressions of the same determinant-one anisotropic angular map.

For initially isotropic free-streaming massless radiation:

\[
\frac{\rho_r}{\rho_{r,\mathrm{iso}}}
=\left\langle \sqrt{S}\right\rangle_{\Omega_*}
=\left\langle D^{-2}\right\rangle_{\Omega_{\rm local}}
=1+\frac85b^2-\frac{16}{21}b^3+O(b^4)
\]

and

\[
\frac{\Delta P_r}{\rho_{r,\mathrm{iso}}}
=-\frac85b+\frac87b^2-\frac{16}{35}b^3+O(b^4).
\]

Wolfram Language evaluated the exact photon-number primitive and differentiated the energy and quadrupole integrands at \(b=0\). The factorial-weighted derivative arrays were \(\{1,0,16/5,-32/7\}\) for energy and \(\{0,-8/5,16/7,-96/35\}\) for the quadrupole: both expansions follow. The sign convention matches `rec_bianchi` PR89 after noting that its \(B=b_{\rm initial}-b_{\rm face}=-b\) for our forward propagation. The exact number identity does **not** assert number conservation in the presence of emission, absorption or crossing the modeled ionizing energy support: such sources/sinks belong in the explicit N and energy ledgers.

## Numerically checked against actual AX08 files

New `number_energy_invariant.py` uses immutable SHA-bound completed ZERO and SHEAR_HALF_PLUS `history.csv` and `feedback.csv`; per case 312,238 actual rows, exact saved proper clocks/scales, local-direction 64-point Gauss–Legendre quadrature (2,048-row vector blocks), and stable `expm1/log1p` cancellation near \(b=0\). Local build/run command:

```bash
OPENBLAS_NUM_THREADS=1 taskset -c 2 python3 research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/number_energy_invariant.py \
    --owner-root /home/cosmosapjw/Dropbox/bianchi/rei_bianchi
```

Observed:
- ZERO: normalized number error 0, saved vs independently integrated energy correction max \(1.6653113041\times10^{-16}\).
- SHEAR_HALF_PLUS: normalized photon-number error max \(2.5370330836\times10^{-17}\), saved vs GL64 energy correction max \(8.0745270699\times10^{-15}\), cubic small-\(b\) energy series maximum remainder \(1.7244015672\times10^{-11}\).
- Both scripts exited 0 with invariant tolerances \(\le10^{-12}\) for number and \(10^{-10}\) for saved energy correction, preserving full input hashes and numerical identity in `number_energy_invariant_result.json`. No solver starts by these numerical tests.

New *native Rust crate* test `rust/rei_microphysics/tests/axbi_phase_volume_invariant.rs` evaluates full signed q family \(0,\pm0.005,\pm0.01\) and four scale-factor snapshots, actual `CharacteristicRay` energy/direction, analytic angle Jacobian, reverse ray map \(J J^{-1}=1\), GL8 number normalization and energy vs existing `isotropic_initial_radiation_moments` Simpson4096. Actual executable test:

```bash
CARGO_TARGET_DIR="$PWD/.ax08_cargo_target" CARGO_BUILD_JOBS=2 \
  taskset -c 2,3 cargo test --offline --locked \
  --manifest-path rust/rei_microphysics/Cargo.toml \
  --test axbi_phase_volume_invariant -- --nocapture
```

Observed **1 Rust test PASS** (\(0\) failures), compile+run wall \(\approx4.36\) s. The one-test scope is narrow and not the full Rust suite or astrophysical chemistry solver.

## Independently retrieved methods and source transfer boundary

- Fleury, Pitrou & Uzan (2015), `https://arxiv.org/abs/1410.8473`: homogeneous Bianchi I null photon ray and observer drift geometry.
- Friedrich et al. (2012), `https://arxiv.org/abs/1201.0602`: multi-frequency H/He ionization/heat accuracy in C2-Ray and stronger temperature-step restrictions.
- Pawlik & Schaye (2011), `https://arxiv.org/abs/1008.1071`: photon-conserving multi-frequency coupled non-equilibrium H/He transfer.
- `rec_bianchi` PR89 `https://github.com/cosmosapjw-quantum/rec_bianchi/pull/89`: independently measured Bianchi I angular phase-volume identity, with its earlier-facing \(B\) convention and related q-even radiation correction.
- `bass_cr` PR71 `https://github.com/cosmosapjw-quantum/bass_cr/pull/71`: positive packet-source-conditioned adaptive q bins bound frozen H/He event/heat interval widths. Requires extra true child moments; cannot recreate them from pooled \((N,U)\) alone or transfer directly to this historical AX08 solver.
- `SOURCE07 C8` owner head `cf472114` demonstrates positive 36→5 source-age-node reduction at a single receiver gas point but out-of-sample opacity perturbation errors. A gas-state-dependent error budget remains necessary before any adopted compression.
- `BASS_HE` PR63, `bass` PR155, and `WU088_HH` PR78 concern distinct warm source, polarized or atomic physics assumptions, with no direct cold-case numerical accuracy transfer.

## DAG continuation

Keep the ongoing authorized MINUS continuation to natural terminal and preserve actual `TERMINAL_RECEIPT` / `RETURN` / `checkpoint`. If complete, compose its original and segment using existing source-epoch-specific `compose_signed_history.py` with the exact observed terminal SHA, preserving raw inputs, before any AX11 science claim. Only then release staged HALF_MINUS according to its actual authority, scheduler state and one-start limits. Disrupted PLUS still needs separate typed recovery. Baseline full signed family and independent AX11 time/energy/angular convergence are prerequisite to admitting resolved shear response; AX12 source/IC variants remain downstream. No self-consistent radiation-stress feedback solver or observer-tail tau is claimed.

## Signed-q amplitude scaling, actual prefix data (additional constructive check)

Additional executable `signed_amplitude_scaling.py` reused five original cases' immutable 200001-row source identities and common 501-point \(\ln a\) coordinate. Instead of comparing different locations of maxima, it evaluated pointwise signed finite differences and reported the two-amplitude ratio **at the same grid coordinate**.

For even \(E(q)\), \(\max|E(.01)-4E(.005)|/\max|E(.01)|\) is \(1.8633708024\times10^{-5}\) for \(x_{\mathrm{HII}}\) and \(2.2541279363\times10^{-5}\) for \(T_{\mathrm{gas}}\). Ratios \(E(.01)/E(.005)\) at the large-amplitude peak are \(3.9999259843\) and \(3.9999509675\), respectively. For the odd \(J_2\) quadrupole, \(O(.01)/O(.005)=1.99999541873\) at its peak, and \(\max|O(.01)-2O(.005)|/\max|O(.01)|=2.29063897\times10^{-6}\). The scalar odd quotients at machine-precision amplitudes are **uninterpretable**, not evidence for large odd coefficients or an asymptotic failure. Numerical errors, time-step refinement and true FLRW departure remain UNKNOWN: these are finite-\(q\) structural diagnostics, not C11/AX11 error certification.

Live MINUS read-back on 2026-10-15 13:28:54 KST: CPU0 process PID1099975 still running, accepted=219060, \(a=0.0941824947806799\), no terminal `RETURN`. Original source/Case-A model and old checkpoints remain intact. No science state is inferred beyond this observed snapshot.
