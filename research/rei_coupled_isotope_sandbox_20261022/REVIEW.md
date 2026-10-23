# Independent review: conditional local isotope sandbox

**Decision: PASS_SCOPED_CONDITIONAL_LOCAL_SANDBOX.** The new mathematical
construction, implementation and observed finite numerical evidence agree
within the frozen execution contract. No substantive current-unit defect was
found and no targeted repair is requested. The admitted scope is prescribed-T
atomic kinetics, its linear-solve component, and local supplied-event/EOS
algebra. Full nuclear/thermal/radiation/cosmological evolution remains outside
this result.

## Independence and evidence boundary

This is one independent review pass for the new sandbox unit. The reviewer
did not author its theory, code, fixtures, diagnostic or acceptance criteria.
Theory was checked before observing execution; actual code and raw outputs
were then read. No diagnostic, old C1/C2 test or physical campaign was rerun.
Only this file and `evidence/INDEPENDENT_REVIEW.json` were written. There was
no delegated review or publication action.

Actual context read: current AGENTS.md; EXECUTION_CONTRACT.md;
THEORY_DERIVATION.md; SOURCES.md; built-in physmath-research-loop **1.0.0**
from `e1/skill-6aa0657100b08191b7d67482d1f97c1d`, including SKILL.md and
RESEARCH_POLICY, THEORY_LOOP, CODING_LOOP, EVIDENCE_AND_HANDOFF and
RUNTIME_AND_LEGACY references. This user-selected context supersedes the
earlier unit's 1.3.0 workflow context for this review. Requested role is
independent Astra-tier scientific review; runtime tool output does not expose
an actual model identifier. The instructional GPT-6 Astra Pro description is
not treated as runtime evidence.

The recorded remote starting head is PR221
`42e44494bd0956756d8c610e75da5b1cafe20d3c`; the restored source directory has
no local Git HEAD claim. C1/C2 findings and the pinned donor are reused within
their old scopes. Seventeen immutable copy checks pass in the producer output.
Read-only inspection confirmed current atomic.py, local.py and diagnostic
SHA256 values and the execution contract match EXECUTION.json. Raw stdout,
stderr, RESULTS.json, EXECUTION.json and TIMING.json were inspected.

## Mathematical assessment

**Shared blocks and the electron derivative.** The donor's adjacent-charge
electronic-equality model gives exactly three common blocks, of sizes 2, 3
and 4, acting on independently stored isotope vectors. Unequal isotope
fractions and initially absent n/T are allowed. With fixed T, spectrum,
n_B and independently supplied fast-electron fraction f,
`B=P+n_B(q.Y-f)R`, `u=n_B RY`, `J_YY=B+u q^T` and `J_Yf=-u` are correct.
This sharing does not identify isotope populations or remove nuclear-source
directions. It does not extend the atomic Jacobian to omitted event or thermal
dependencies.

**Inverse and denominator theorem.** Sherman–Morrison has the correct sign
for `I-hJ=(I-hB)-huq^T`. I independently subtracted adjacent adjoint equations
to obtain the stated difference system. Its interior column dominance margin
is one; endpoint columns add nonnegative boundary rates. Its inverse is
nonnegative and its diagonal contribution makes each adjacent difference
strictly positive. Downward recombination then gives
`q^T M^-1 u=-n_B sum(alpha*Y_upper*delta)<=0`, hence **d>=1**.
This proof applies to Y>=0, h>=0, n_B>=0 and nonnegative thermal electron
density. It also applies to the fixed-f abundance partial under those signs.
It does not assert conditioning of the full matrix, nonsingularity for signed
trial states, or a denominator bound for an augmented nuclear/thermal system.

**Positive midpoint.** Both frozen exponentials are nonnegative and preserve
each isotope total in exact arithmetic. Expanding the midpoint coefficient
gives the missing `u(q^T F)` term in the h² coefficient and therefore
`Ynew=Y+hF+h² JF/2+O(h³)`. The second exponential acts on the original Y.
The primary full text of Blanes–Iserles–Macnamara, arXiv:2102.08242v2,
§3.3 equation (3.8), was independently opened and is the same method. The
result is a fixed-input atomic-only order statement, not an order or positivity
claim for an unspecified nuclear/thermal composition.

**Onset, scaling and interpolation.** Absolute abundance and fixed positive
scaling are regular at zero; polynomial mass-action partials are evaluated by
reducing powers, avoiding division by absent reactants. The factorial for an
identical binary pair is correct. A common scale within an isotope commutes
with its atomic block; arbitrary component scales remain valid similarity
coordinates but need not preserve shared factorization. The log-linear
coefficient remainder and `expm1(M dx²/8)` relative bound are correct given
an actual interval curvature bound. Three saved knots do not supply that
bound. Exact knots, declared zero intervals, absent channels, zero reactants
and representational underflow remain distinct.

## Implementation assessment

PreparedAtomic obtains P and R from the pinned donor and excludes D. Its
physical scalar/batch RHS, analytic Jacobian and fast-electron column implement
the stated expressions. The structured solve packs isotope and correction
columns into shared Thomas solves, checks pivots/denominator/finiteness and a
backward residual, and records a dense fallback when that route is unsafe.
The finite physical solve grid used no fallback; no measured fallback-accuracy
claim is added. Dense remains the actual default at this dimension.

The midpoint uses one common small exponential per element per stage and
does not clip or renormalize. ResolvedEvent computes log flux before exp,
keeps log/status information on underflow, handles zero-reactant derivatives
and requires baryon balance and a supplied energy ledger. The supported
interface takes already resolved channel coefficients; parent/probability
metadata is explicitly rejected. It does not silently assume normalized
branch weights. Beta uses the evaluated lambda with a labelled manufactured
ledger, not a physical beta energy partition. Event reservoir, charge and
nucleus sources remain separately available.

The EOS and outer transform use the supplied translational energy source,
both nucleus/electron particle changes and the explicit f/fdot terms; H and
population scale are applied once at the outer boundary. Missing thermal
closure is not replaced by a default physical zero.

## Observed numerical results

The first and only diagnostic reports **156 PASS, zero failures, exit 0**.
It covers 54 atomic grid states, 27 structured linear solves, four midpoint
trajectories, one atomic Radau oracle and six scaled scalar trace solves.
Old C1/C2 invocations and cosmological IVPs are both zero.

| Quantity | Observed value | Criterion |
|---|---:|---:|
| Atomic RHS algebra residual, maximum | 1.8515098438111052e-16 | <=512 epsilon |
| Atomic Jacobian algebra residual, maximum | 0 | <=512 epsilon |
| Complex-step Jacobian residual, maximum | 1.426903633051093e-16 | <=1e-10 |
| Fast-electron column residual | 2.9873394690700524e-17 | <=512 epsilon |
| Linear backward residual, maximum | 2.447433391576442e-16 | <=1e-12 |
| Linear dense-reference forward error, maximum | 1.407471973264549e-15 | <=1e-10 for cond<=1e8 |
| Largest measured infinity-norm condition number | 1068.3455842348608 | recorded conditioning |
| Structured denominator range | 1.0000000277068966–1.7167530503787187 | physical theorem d>=1 |

Here `512 epsilon=1.1368683772161603e-13`. Midpoint final isotope-weighted
errors at N=16,32,64,128 are 2.6482392222776596e-6,
6.588415156301833e-7, 1.6430642106859244e-7 and
4.1026010944314016e-8. Observed orders are 2.0070300787020052,
2.0035426048995997 and 2.0017780721554916. Maximum isotope conservation
error is 1.0728597497579638e-15; the smallest observed isotope fraction is
positive (0.10604818870294462).

For both 1e-104 and 1e-120 scales, the scalar source-loss problem starts at
exact zero. Maximum component-relative errors decrease from approximately
9.7254e-10 to 1.1233e-11 to 1.1167e-13 as Radau tolerance is tightened.
These are explicit scalar scaling/onset tests, not new nuclear trajectories.
The wrong rank-one, identical-reactant symmetry, beta-separation and particle-
count constructions are detected, while missing/invalid physical-input paths
return the specified errors. The finite tests do not create missing providers.

## Timing, figures and termination

Seven local timing batches at one BLAS thread give median prepared/rebuilt
RHS improvement **3.7803x** and batch64 vector/scalar improvement **36.2515x**.
The structured/dense solve speed ratio is **0.2952**: dense is faster and is
correctly retained as default. These are observed costs of the implemented
methods at dimension 21, not theoretical or universal speed guarantees.
Setup costs and repeat ranges are recorded separately; batch64 calls must
be compared to other batch64 calls, not to a single-state linear solve.

All three PNGs were visually inspected: labels and axes are readable, no
material clipping was found, midpoint data follow the displayed N^-2 guide,
and trace curves coincide as expected from the selected scaling. Timing error
bars show the actual repeat ranges. The Matplotlib cache warning is preserved
in stderr; its automatic temporary cache allowed figure generation to finish.

Measured diagnostic-body wall time is 10.399398439003562 s and CPU time is
10.278435498999999 s; these timers start after imports. Peak process RSS is
111128 KiB. The reported values lie below the contract's 180 s wall/120 s
CPU/1 GiB caps; the body timers are not a measurement of complete process
startup time.
No production/provider closure expansion, extra experiment or repair is
required for the current scoped admission. Continue by composing explicitly
supplied event and energy models with the validated local components under a
new finite integration contract; preserve their domain and numerical limits.

## Separately authorized onset coverage and replay helper

After the baseline run, the parent authorized two targeted source-onset
checks; the baseline diagnostic and its three scientific source files were
not rerun or changed. I read the added script, raw targeted JSON/stdout/stderr
and hash identities. Both manufactured `DII+DII -> He3III+n` and
`DII+DII -> HII+TII` channels start the target at exact zero and yield positive
source `1.7359929831205052e-12`. Their coefficient is explicitly supplied,
the identical-pair divisor is 2, the polynomial flux relative error is
`1.5122924563072915e-15`, and exact integer baryon/charge residuals are zero.
The zero-Q/zero-energy ledgers are labelled manufactured; these cases do not
establish empirical nuclear rates or energy partition. The two targeted
checks pass with exit 0, no IVP and no full diagnostic replay. Accounting is
**156 baseline checks plus 2 separately executed targeted checks**.

I also read `run_fresh.sh` and `FRESH_ENTRYPOINT_CHECK.json`. The helper
copies the unit to a new temporary artifact directory, moves existing
evidence and figures aside, and delegates future execution to the unchanged
runner followed by the targeted script. Recorded syntax/help/prepare-only
checks exit 0 and start no scientific execution. Read-only inspection confirms
the helper and targeted-script hashes match their records and the prepared
copy preserves baseline RESULTS bytes. This verifies preparation, not a
completed fresh scientific replay. The scoped admission is unchanged.

## Final documentation scope check

Within this same review pass, I read the completed REPORT_KO.md, README.md,
RESUME.md and DAG.json. Their numbers, separate baseline/targeted accounting,
conditional physical scope, midpoint domain, manufactured-ledger limitations,
timing comparisons and helper-validation boundary agree with the observed
evidence. DAG C10 distinguishes scientific handoff from publication and storage
acknowledgments. No publication or backup success is certified by this review.
No concrete correction remains. This independent review is concluded.
