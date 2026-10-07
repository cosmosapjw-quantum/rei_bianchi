Publication note: quoted hashes identify archived original bytes; current publication hashes are listed in ../PROVENANCE.json.

# Collisionless FLRW transport comparison: frozen contract candidate v1

Historical pre-run scientific contract. Completion and limitations are recorded in REPORT.md and INDEPENDENT_REVIEW.json.

## Scope and exact problem
Research-only 1D diagnostic, no production edits/migration, no chemistry/source/background history, no uploads. Independent nonzero-initial-photon control, separate from production zero-initial budgets. s=ln(a/a0), x=ln(E/13.6eV), x in [0,L], L=ln(100/13.6), g_s-g_x=0, h=g/E, h_s+(-Eh)_E=0. No upper inflow. g(s,x)=g0(x+s).
g0(x)=C exp(-1/(1-z^2)) for |z|<1, zero otherwise, z=(x-.65)/.25. C normalizes integral g0 dx=1. This is C-infinity and supported in [.4,.9].
Nout'=g(s,0), Eout'=13.6*Nout', W'=U. N+Nout=N0; U+Eout+W=U0. Outgoing energy is energy at threshold crossing, not initial energy. Oracle uses independent Python mpmath at 60 decimal digits; no method state is replaced by oracle density.

## Methods and initial projection
All methods use the same n uniform comoving-x panels / physical-E log-spaced faces. GL8 per initial panel gives positive node weights wi=dx/2*qi*g0(xi); normalization C comes from independent oracle, and methods do NOT renormalize their projected stocks. Initial numerical N0 and U0, and analytic errors, are recorded independently.
A: whole-Gauss-node characteristic stock. Fixed comoving xi, weights wi, physical x=xi-s. Entire wi exits when s reaches xi. Exact event crossing energy and analytic characteristic work wi*(Einitial-Ecurrent_or_threshold), using expm1 where appropriate. This is a standalone mechanism diagnostic, not a claim to replay all production-solver logic.
B: positive comoving P0 reconstruction on each initial panel, Gbar=sum(wi)/dx. Active partial-panel mass, energy and independent characteristic work are integrated analytically; no stock is dropped wholesale. This is exact transport of the DECLARED reconstruction, not the initial analytic bump.
C: physical-E P0 FV, h=a. Cell number initialized by sum(wi); U=Emid*DeltaE*a. Flux at interior face F=-Eface*h_from_right; upper flux 0, lower outflow interior. a'=-(FR-FL)/DeltaE. This number-conservative diagnostic may fail the physical-energy ledger; preserve/report it.
D: physical-E P1 DG, h=a+b*r, r=2(E-Emid)/DeltaE. Initial a=Ncell/DeltaE and b=6*(Ucell-Emid*Ncell)/DeltaE^2 from the same GL8 initial nodes. Exact volume moments: Ncell=DeltaE*a; Ucell=Emid*DeltaE*a+DeltaE^2*b/6. Upwind face density is the right cell's left endpoint a-b. Shared face flux once. a'=-(FR-FL)/DeltaE; b'=-3*(FR+FL)/DeltaE-6*Ucell/DeltaE^2. Run without and with endpoint cell-mean positivity limiter.
Limiter: m=a-|b|; if m<0 and a>=0 use theta=min(1,a/(a-m)), b<-theta*b, preserving a. a<0 is a recorded hard positivity failure, never silently clipped. Apply after initial projection and each SSP stage. Log exact DeltaU=DeltaE^2*Delta b/6. This changes physical energy; no ledger repair. Number and energy weak tests are 1 and E, not 1/E.

## Time integration and independent refinements
C,D use SSPRK2 on full state including Nout, Eout and W, with the identical stage boundary flux and W'=U(stage). Stage 1 y1=y+dtL(y), limit y1; stage 2 raw=.5*y+.5*(y1+dtL(y1)), limit final. Limited-DG accumulated energy modification weights are .5*DeltaU_stage1+DeltaU_final; also record absolute modifications. Initial limiter change is separate.
Nominal dt=c*min(DeltaE/Eright). c=.15, .075, .0375 (all below conservative P1 sufficient c<=.5). Each common output interval is subdivided into ceil(interval/dt) equal steps, so all epochs match exactly.
Space series n=32,64,128,256 at c=.075. Time series n=128 at c=.15,.075,.0375. Duplicate case only run once. A/B are time-exact, run once per n; no fake temporal convergence series.
Common s outputs [0,.2,.4,.5,.6,.7,.8,.9,1.0]. Scalar shape values use same epochs. No changes to resolution/epochs/tolerances based on attractive results.

## Error/diagnostic records
At every epoch: N,U,Nout,Eout,W; number residual normalized by each method's N0; physical-energy residual normalized by each method's U0; each initial projection and initial limiter error versus oracle; Nout and Eout error versus oracle (normalize N0=1 and true U0); minimum density and total negative mass; limiter application count and signed/absolute energy modifications; actual step count and measured runtime.
Continuous density methods B/C/D: L1=integral |g_h-g_exact| dx / N0 (same as integral |h_h-h_exact|dE), evaluation quadrature independently checked GL8 versus GL16. A is an atomic measure, so continuous-density L1 and density minimum are explicitly NOT APPLICABLE, rather than inventing a density. For comparison across all methods additionally report common 32-bin coarse-mass L1=sum |bin_mass-bin_mass_exact|, always labeled coarse-grained, plus maximum output cumulative-outflow error. Stock A negativity instead means minimum weight. B density min includes zero outside pulse.
Independent semidiscrete derivative checks and local algebraic tests distinguish space from RK time defects. Do not infer work from ledger closure. Balance thresholds (diagnostic certification only): |number residual|<=5e-12; unlimited-DG compatible energy residual<=5e-12; characteristic A/B energy residual<=5e-12. FV and limited DG energy residuals are observations, not required passes. Limiter accounting agreement with residual<=5e-12. Positivity tolerance for roundoff reporting 1e-13*max(1,max|h|); raw min always retained. No fabricated success threshold on L1; report rates and failures.

## Test-first acceptance before benchmark
1. Verify exact P1 moments against independent polynomial integration and weak derivative identities for arbitrary positive/negative slopes and independent face fluxes.
2. Verify FV preserves shared-flux N and exposes its energy residual rather than making W absorb it.
3. Verify SSPRK2 number/energy ledgers with no limiter and stage-compatible flux/work.
4. Initially empty P1 cell with tiny upper-face inflow: incoming U/N=Eright, negative reconstructed endpoint; limiter preserves N but changes U. Show analytically and numerically; no transport oracle substituted.
5. Partial-panel integrals and independent characteristic work obey both ledgers, including threshold exactly on a node/face, before/after support, all exited and zero step.
6. Negative cell mean is rejected; theta limiter preserves nonnegative mean and endpoint positivity; weighted stage limiter DeltaU matches energy residual.
7. Independent high-precision oracle identities and 60->80 digit selected-value crosscheck; GL8->GL16 diagnostic quadrature check. Numerical failures are saved, not erased by altered tolerance.

## Budget, accounting and output
Fresh total numerical budget <=120 CPU seconds, <=180 wall seconds; one numerical process at a time; each process <=512 MiB address space; task output including builds <=32 MiB; stop/save if reached. Rust standard library only; existing verified Rust toolchain, no installs/dependencies. Python standard library plus already-installed mpmath only for independent oracle/assessment. No long PDE solve.
At most 2048 live initial GL8 sites (n=256); initial sites released before live evolved DG arrays. Diagnostic integration streamed with <=16 quadrature points live per cell. Distinct-node count is NOT scalar-storage count. Record all arrays explicitly: face vector n+1; a,b initial/current/stage/RHS/output vectors as actually implemented; no array omission by calling vectors one grid.
Save contract/hash, derivation/source identities, red tests, green tests, oracle/hash, per-case output incrementally, budget receipt, complete failures, assessment and independent review. Any substantive contract adjustment is versioned and re-reviewed before implementation.
