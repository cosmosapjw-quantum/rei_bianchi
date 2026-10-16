# Unit5: restored Krylov continuation and a resolvent residual diagnostic

Frozen 2026-10-16 from PR151 head `7e07012`; immutable runner intake SHA256
`b9a14d1bfa192da17b7c2a6dfa20560964d553b3c0ba30343a45bb90ee09db7a`.
This is a specification, not evidence that a production continuation ran.

## Scientific object and historical boundary

Keep the same saved common orbital space, normalized working ground state g,
parent i, E0, Q=I−gg†, u=Qi/√W and K=Q(H−E0)Q. Energies are Hartree;
all other quantities use atomic units. H uses exactly repair001's real
h→(h+hᵀ)/2 and packed ERI→(ERI+ERIᵀ)/2 before the frozen V6 raw_action.
Do not change the underlying model, ground state, direct-moment policy,
milestones, broadening widths, spectral grid or refinement acceptance.

The actual Unit4 checkpoint has length 64, 67 repaired-run actions and 86
known cumulative actions including the failed first run. Terminal cumulative
actions are UNKNOWN within [86,160]. Its allocation expired at
2026-10-16T01:51:37.258157Z. Neither restart nor a new code version resets this
deadline or replaces the unknown terminal count by 86. This unit authorizes
only local dense tests and preparation, zero new NCP Hamiltonian actions.
A future production execution requires a separately explicit allocation
contract; its newly charged actions must be recorded separately from the old
historical interval. No production success or convergence is claimed here.
The archived actual checkpoint SHA256 is
`1a056d3095f70c6f2473e1e242b1e0eb329427688df58a85cfdb2667938f704f`.
That large checkpoint is not present in this sandbox; actual checkpoint
compatibility is NOT_RUN. Synthetic legacy-format serialization is testable.

Implement a complete future run/resume CLI accepting the checkpoint plus an
explicit new-allocation config. A prepared template may propose 7200 seconds,
24 GiB, 12 OMP threads, 1 BLAS thread and at most 70 newly charged H actions
(3 reconstruction + 3 seam + up to 64 extension), max length 128. Mark the
template authorized=false and execution=NOT_RUN. Execution requires a separate
explicitly authorized allocation with a unique allocation ID, issue/start time,
new absolute deadline and these ceilings; absence, false authorization or
expiration fails before any H action. The CLI must never infer that allocation
from the old checkpoint or silently renew a deadline. This specification does
not itself authorize activating that template. If n new actions are eventually
charged, campaign cumulative actions remain the interval [86+n,160+n], unless
new evidence resolves the old terminal count.

## Restoring the state

Read V, KV, ground, u, next_vector and metadata_json with allow_pickle=False.
Require common dimension, finite numerical entries, 1≤m≤128, V/KV shape
(dimension,m), scalar finite nonnegative next_beta, and a consistent integer
metadata length. Enforce the frozen input hashes and operator convention.
For the actual legacy checkpoint accept its recorded repair001 runner hash
through an explicit old-runner→new-resume implementation mapping, not equality
to the new file hash. Record both identities. A runner hash difference alone
is BYTE_IDENTITY_MISMATCH, not a scientific operator mismatch. Unknown legacy
runner/operator combinations are rejected until explicitly mapped.

Compare saved g and u to freshly prepared working arrays in vector 2-norm
at 1e−10, and V[:,0] to u at 1e−10. Enforce the inherited Gram (1e−9),
ground leakage (1e−10), compressed anti-Hermitian (1e−10 scaled), mass,
eigensystem and direct-moment gates. Check next_vector's unit norm and
orthogonality to V and g at 1e−9 for non-breakdown. Reconstruct the last
two-pass fully reorthogonalized remainder from cached KV[:,m−1] using the
same Q/MGS/Q ordering. The prior-beta term lies in span(V), so may be omitted
for this check; compare the reconstructed remainder to next_beta*next_vector
at 1e−9 max(1,||KV[:,m−1]||). This is a seam consistency test, not a replay.
For breakdown require next_beta≤1e−12 max(1,||KV_last||) and the saved next
vector to be zero to 1e−10; never divide by that beta or continue the chain.

Recompute C=V†KV, J=(C+C†)/2, diagonalization, weights and all spectra from
the cached arrays. Recompute direct moments from u and KV[:,0]. Validate any
recorded direct moments at the inherited 1e−8 scaled tolerance. Recompute
the previous milestones 16,32,...≤m from prefixes, with their own remainder
computed from cached columns, so comparison at 128 is actually against 64.
Never trust an archived compressed matrix or spectral array instead of these
calculations. This step requires zero H actions.

Legacy checkpoints omit the historical reorthogonalization correction list.
Recover it from the matching milestone JSON when available and structurally
consistent. Otherwise preserve an explicit historical-unknown prefix (null
entries or separate provenance/status); never manufacture zeros. Newly
computed corrections are numeric and indexed from m onward. These historical
corrections are diagnostics, not needed to continue the recurrence.

Allocate V/KV to the chosen cap, copy the m columns, set v=next_vector and
previous_beta=next_beta, and execute the unchanged recurrence starting with
zero-based j=m. For the actual checkpoint the first new Krylov action is
K v_65, j=64; it is not K v_64 and does not repeat the first 64 actions.
Preserve two-pass full reorthogonalization against all restored and new
columns. A valid saved stopping decision (happy breakdown, refinement met,
or negative-node interpretation hold) is honored before any new action.

## Reconstructed-operator validation before any future production extension

The existing nine reconstruction gates are rerun unchanged, charging their
three H(i), H(g), H(u) actions. In addition charge three K actions against
the restored cache: x=V[:,0], x=V[:,m−1], and x=Vc for
c_j=(-1)^j (j+1)/sqrt(sum_{k=1}^m k²), j=0,...,m−1.
Compare each fresh action with KVc (using the corresponding coordinate vector
for first/last). Require norm discrepancy ≤1e−9 max(1,||fresh||,||cached||),
and report absolute and scaled discrepancies. Do not normalize Vc separately.
These deterministic checks sample an operator seam; they do not prove every
cached action correct. Exact immutable input binding plus unchanged operator
construction and these checks are the finite research-integrity boundary.
The action budget must charge all six pre-extension actions, including an
action whose post-action deadline check fails. A failure forbids extension,
preserves the checkpoint and identifies the failed gate. No replay of 64
actions is required or permitted as an automatic verification expansion.

## Resolvent diagnostic

For z=ω+iη, η>0, define t=(zI−J)^−1 e1 and the compressed scalar
m_J(z)=e1†t. The plotted density remains S_J(ω)=−W Im(m_J)/π, identical to
the Lorentzian sum from J. Define E=KV−VJ, d=u−Ve1 and
r=d+Et=u−(zI−K)Vt. These identities assume the cached KV represents K V.
For self-adjoint K, ||(zI−K)^−1||≤1/η, hence

|u†(zI−K)^−1u − u†Vt| ≤ ||u|| ||r|| / η.

Because finite arithmetic does not make V exactly orthonormal, retain
δ=(u†V−e1†)t. The diagnostic bound for the same compressed scalar used in
the spectrum is

B_m(z)=||u|| ||d+Et||/η + |δ|,
|m(z)−m_J(z)|≤B_m(z),
|S(ω)−S_J(ω)|≤W B_m(z)/π.

In the exact initial-coordinate case d=0 and δ=0 this reduces to
||Et||/η and W||Et||/(πη), respectively. This derivation does not use the
last recurrence beta as a substitute for E and remains valid for a Hermitian
J obtained by symmetrizing a slightly non-Hermitian C. Do not silently use
E=KV−VC with the J resolvent. The full residual includes that difference.

Compute residual norms directly for small dense tests. For a large cached
basis, an optional efficient implementation forms A=[d,E], its Gram A†A,
and evaluates [1;t]†A†A[1;t], with a stated roundoff-clipping diagnostic for
tiny negative values. A materially negative quadratic form is a failure.
This is a floating-point a posteriori diagnostic conditional on self-adjoint
K and cache accuracy; it is not outward-rounded interval certification.
It creates no new spectral-convergence PASS rule. Report pointwise bounds,
maximum bound for each η, and optionally the trapezoid integral of the bound
over the grid (a grid diagnostic, not a certified continuum integral bound).
No inference of ionization, energy-normalized continuum or basis closure.

Moment stability alone is insufficient for spectral convergence: the unit-mass
measures ½δ₁+½δ₃ and ¼δ_(2−√2)+½δ₂+¼δ_(2+√2) share mean 2 and variance 1,
but have different CDFs and broadened spectra. This explains why passing
moment gates does not override Unit4's failed L1/CDF refinement.

## Bounded validation and stopping rule

Use deterministic small dense Hermitian K with a separately diagonalized
full-space reference. Run an uninterrupted chain and an actually stopped,
serialized, reloaded and extended chain under the same algorithm. Compare
resolvents/spectra, direct moments and invariant subspace projectors at
1e−8 scaled; compare basis vectors only as an additional diagnostic. Do not
require pole/weight byte identity, especially in degenerate eigenspaces.
Record actions before/after the seam; restoring and recompressing consume
zero actions, extension consumes exactly one action per added column, and
optional operator seam verification consumes exactly three. Reconstruction
actions are tested separately or together with a toy H fixture.

Tests must cover a nontrivial stop/resume continuation, malformed shapes and
nonfinite arrays, immutable/operator mismatch, corrupted cached last action,
budget exhaustion and expired deadline before a new action, happy breakdown,
historical unknown corrections, and a changed runner hash accepted only by
the explicit semantic mapping. Test the residual bound against an independent
dense resolvent for a truncated chain and nonzero initial-coordinate defect;
require measured error≤bound+1e−10 max(1,|reference|). Include at least one
complex Hermitian fixture if supported by the existing generic API, and a
case with slightly non-Hermitian C to catch accidental C/J mixing. No claim
that the bound is sharp or monotone in Krylov length is required.

Stop after this bounded suite and one independent scientific review. One
targeted repair is allowed if the reviewer identifies a concrete scoped
defect. Do not expand into further governance or remote execution. Local
validation is PASS only for demonstrated behavior; production continuation
remains NOT_RUN and actual Unit4 refinement remains HOLD.
