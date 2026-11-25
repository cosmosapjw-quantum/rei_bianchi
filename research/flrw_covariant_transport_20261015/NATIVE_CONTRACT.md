# Covariant native transport: active scientific contract

Baseline: PR150, `8aa6cd081f218e3a4ff6180a547c790df234a073`.
This unit replaces only the photon representation and its dependent source,
reaction, comparison, output and restart interfaces. The physical source,
cold H/He rates, background, IC choices and acceptance thresholds are retained.
The earlier 28 checks and full histories remain evidence of their original
implementations; they are not replayed or relabelled as new transport evidence.

## Selected method

Use fixed covariant reference-energy cells and symmetric reference rays. Each
cell stores nonnegative photon count N, reference first moment Uq, and actual
populated support. Geometry changes E=R(a,mu)q and the observed direction,
but never remaps the stored spectrum onto physical-energy nodes. Account for
photon redshift work from the actual energy difference. Retain inert photons
below the ionizing band in these same cells; they are not absorption events.

Source injection integrates the frozen spectrum over mapped cell intersections
with positive GL8 source subcells. Apply the existing local-isotropic angular
Jacobian normalization exactly once. Both source ledgers use the moments
actually injected. Do not invent child moments from a cell centroid.

For each chemistry stage, reconstruct a bounded positive exponential from N,
Uq and support, split at actual cross-section fit cutoffs divided by R, and
cache a positive quadrature before Newton. A support delta is evaluated at its
actual energy. Near-endpoint means require a resolved positive reconstruction,
not clipping or replacing a broad support with a delta. A documented
dimensionless exponential tail truncation at 48 has a discarded shape-mass
bound exp(-48); moment matching must still preserve stored N and Uq.

Quadrature must reproduce count to 64 binary64 eps times N and first moment
to 128 eps times max(abs(Uq), N times support width). These are internal
representation checks, not relaxed physical ledger tolerances. A finite cap
must produce a typed failure rather than an invented spectrum.

Within each existing four-unknown cold Newton trial, use the same quadrature
nodes for BE survivors, photo rates, heating, and returned N/Uq:

    n_l = w_l / (1 + dt*c*sum_j(n_abs_j*sigma_j(R*q_l)))

The event owner remains the coupled chemistry RHS. No frozen-gas exponential
absorption or second gas-photo update may be added to this stage. Fit cutoffs
(13.60,24.59,54.42 eV) remain distinct from binding energies in HHeModel.

This is a closure-controlled finite-volume/two-moment method. It does not
uniquely recover the true spectrum from two moments. Threshold-split adaptive
quadrature and geometric grid refinement are selected now; FEM and dynamically
splitting cells without true child information are not selected. The reason
is the direct positive N/U conservation contract and bounded storage, not a
claim that other discretizations cannot work.

## Native integration and restart

Default reference grid: 128 logarithmic cells, q in [13.6,512] eV; validate
every source intersection against that domain. Use explicit grid-resolution
configuration for refinement. Carry N/Uq/support in a new checkpoint version.
Full-versus-two-half comparison uses matching q cells for N and actual energy
moments. Preserve gas fractions/thermal terms and all original normalizations.
Output spectra report actual physical support and moments. A changed source
or representation starts fresh outputs; no old full-history resume.

The local target remains 1e-5, strict local ceiling <2e-4, Newton scaled
residual <=1e-11, per-step ledgers <=1e-10, cumulative ledgers <=1e-8,
and normalized reflection-parity tolerance 1e-12. The cold provider domain,
no-clipping rule, and sole adiabatic/CMB/escape owners are unchanged.

## Changed-dependency execution and admission

1. Test actual-energy HeII threshold regression, positive moment matching,
   source N/U, BE event/energy identities, geometry invariance, paired rays,
   source support, checkpoint round trip and coupled driver ownership.
2. Run a fresh short FLRW interval with the conditional REC IC already bound
   in PR150. Preserve every first failure. Use q cells128/256/512, time targets
   1e-5 and2.5e-6, and angular8/16 as separate, labelled controls. The selected
   short interval is z20 to19.8; if it fails to finish within its cap, record
   incomplete screening and repair the specific numerical cause.
3. Before observing these results, freeze a conditional short-interval screen:
   relative differences of gas fractions (floor1e-5), actual Tgas (floor1 K),
   total photon N/U (floors1e-8 in their per-H units), and accumulated photo
   events (floor1e-8 per H) must be <=1e-3. For the three q grids the finest
   difference must not exceed1.1 times the preceding difference, unless both
   are already below1e-8. This screen is an empirical launch criterion; it is
   not a full-history accuracy certificate. Preserve raw Gamma diagnostics as
   well; zero false-threshold events are checked separately by the delta test.
4. Independent review of the changed code and measured screen opens a fresh
   conditional full-history run on actual NCP, with a refinement companion.
   Full-history convergence, thermal/species consistency and report/plot
   claims remain pending until those histories actually finish and are read.

New short runs are capped individually at600 wall seconds,20000 accepted
steps,65000 tentative starts,5M RHS and256MiB output. At most two scientific
cases run simultaneously. Preserve charged wall time and failed attempts.
One diagnosed defect authorizes one targeted repair and its dependent rerun;
unrelated completed tests are reused. This unit does not inherit an unused
allocation from historical benchmark launchers.

NCP full campaign: actual observed64CPU/135050518528-byte RAM host; at most
two scientific cases at once, initially one native thread each,8GiB address
space per case,4GiB output per case, and43200 seconds cumulative wall from
first full launch with300 seconds reserved for closeout. Do not reset the
campaign deadline on resume. Native counters remain800000 accepted,
2600000 tentative starts and200M RHS per full case. Case parallelism is
permitted; no unmeasured64-way speedup is claimed.

## Parallel isotope unit

The first D provider is explicitly named
GRACKLE_3_4_1_H_EQUALITY_D_ATOMIC_V1. It uses source-bound H-rate equality as
a conditional model and a supplied D binding threshold consistently for
photoionization, CI, RR escape and D/H CX. It is not an isotope-exact rate
calculation. No default abundance, matching REC/BBN donor, or cosmological D
history is inferred. The separate isotope-native RHS and event/energy tests
may be admitted before integration into the full cosmological solver.

PASS always opens the next executable action above. Infrastructure permission
is already present; remaining representation or numerical failures must be
reported as their actual dependency, never as a new permission request.
