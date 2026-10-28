# Independent theory and static preparation review

Unit: `rei_caloric_directional_pullback_20261028`  
Native reviewer task: `/root/current_repo_census`  
Role: distinct-author independent scientific/static reviewer. This reviewer performed the earlier source census but did not author this unit's contract, proof, implementation, or tests. No blind-isolation claim is made. The shared filesystem and prior source-intake context are explicit. Requested/host instruction tier is Astra; no separate backend model identity is inferred.

## Initial verdict — theory only, preserved before code inspection

**R6: PASS_SCOPED_INDEPENDENT_THEORY.** The supplied represented monotone piecewise-affine caloric inverse has the stated interior differential, directional knot formula, endpoint-domain restrictions, equal-slope interior-knot differential, matched moving energy-coordinate covariance, and composition with an explicitly supplied differentiable callback. The result is a constructive first-order statement for the declared finite branch. No theory defect requiring repair was found.

This verdict was recorded after reading the full `THEORY_AND_CONTRACT.md` and before semantically reading the new implementation or its test body. It does not grant runtime acceptance. At this point C9 static inspection is pending; C6–C8 are **NOT_RUN**. Source/data review, exact algebra on paper, and implementation execution are different evidence.

### Actual review method

I independently differentiated the barycentric interpolation identities, took exact one-sided limits at a moving knot, matched the two smooth formulas at an equal-slope knot, checked the feasible parameter domain, and manually expanded controls A–H. No Python scientific code, imports, test command, CAS evaluator, plotting, provider calculation, or numerical source calibration was executed.

The workflow1.0.0 R6 definition permits an independent derivation/back-substitution/limit-case review appropriate to the claim. Its C9 definition requires inspection of actual code, algorithm/error claims and independent reference construction. The pending code addendum will apply that scope without treating authored tests as executed results.

## Independent mathematical checks

### D1: open segment

Write `DeltaU=U[i+1]-U[i]>0`, `DeltaT=T[i+1]-T[i]>0` and `w=(E-U[i])/DeltaU`. Direct quotient differentiation gives

\[
\dot w=\frac{v-(1-w)b_i-wb_{i+1}}{\Delta U}.
\]

Substitution into `T=(1-w)T[i]+wT[i+1]` yields

\[
\dot T=(1-w)a_i+wa_{i+1}
       +\frac{v-(1-w)b_i-wb_{i+1}}{s_i},
\qquad s_i=\Delta U/\Delta T.
\]

Both knot-motion terms are present, with the negative energy-knot coefficients required to hold the target energy fixed. Taking `a=b=0` reduces to `v/s_i`. Moving all temperatures by the same amount gives that same temperature translation. A common energy translation of the target and every energy knot cancels. Dimensions are K per declared parameter throughout.

Strict nominal temperature/gap inequalities provide an open neighborhood for any fixed finite direction. An energy strictly inside the selected segment remains inside it for sufficiently small parameter values.

### D2: moving knot and domain

At `E=U[j]`, the signed relative motion is `q=v-b[j]`. For positive parameter and `q>0`, the exact nearby right-branch expression is

\[
T_j(\epsilon)+\epsilon q/s_j(\epsilon).
\]

Its derivative is `a[j]+q/s[j]`; the left branch gives `a[j]+q/s[j-1]` for `q<0`. Under the declared affine parameter family, `q=0` keeps exact target/knot equality and gives `a[j]`.

At the lower and upper endpoints the feasible signs are respectively `q>=0` and `q<=0`. Outward directions have no value in the stated map and must be refused. The contract correctly distinguishes the explicit affine family from a general differentiable family: a zero first-order relative motion does not alone certify second-order feasibility at an endpoint.

### Equal slopes and linearization

At an interior knot with unequal adjacent slopes, the fixed-knot directions `v=1` and `v=-1` produce `1/s_right` and `-1/s_left`. The lack of oddness rules out one linear differential.

When the nominal adjacent slopes are equal to `s`, the two adjacent formulas have the common gradient

\[
a_j+(v-b_j)/s.
\]

This is a full first differential in the knot/target coordinates, not merely a coincidence for fixed knots. In a sufficiently small neighborhood the positive knot gaps bound the denominators. A slope change is first order in the coordinate perturbation and multiplies a first-order target-to-knot separation; that discrepancy is second order. The two rational branch formulas therefore share the same first-order remainder estimate at the joining surface.

The endpoint API's refusal to call a relative/one-sided domain derivative an unrestricted two-sided derivative is consistent, including a globally affine branch.

### Matched moving energy coordinates

For `U'=A U+B`, `E'=A E+B`, `A>0`, the nominal weight is unchanged and the slope becomes `A s`. Using

\[
b'_i=A b_i+\dot A U_i+\dot B,\qquad
v'=A v+\dot A E+\dot B
\]

leaves the residual numerator multiplied by `A`: the `dot A` term cancels by the interpolation identity and the `dot B` term cancels because weights sum to one. At a knot `q'=A q`, preserving side and endpoint feasibility. This is covariance of the first-order coordinate description. Finite products of independently affine parameter families can have quadratic terms; no finite-parameter equality beyond the specified first-order claim is needed.

### Supplied callback

For a differentiable supplied `f(z,T)`, the ordinary first-order expansion gives `df=J_z dz+f_T dT`. Composing it with a one-sided directional temperature at a kink is valid but generally yields a directional map, not one common Jacobian in all directions. A missing temperature column is a missing input, not a zero column inferred from the unrelated frozen-rate chemical model.

## Manual exact control check

| Control | Independent calculation | Result |
|---|---|---|
| A | Segment1 has `w=1/2,s=3`; interpolated temperature motion is `1/2`, interpolated energy motion is `1`. | `dT=1/2+4/3=11/6`. |
| A, rational path | Combining `(2-e)+(3+7e)(2+3e)/(6+6e)` gives `(18+29e+15e²)/(6+6e)`. | Exact forward error `2h/[3(1+h)]`; centered error `-2h²/[3(1-h²)]`. |
| A, feasibility | The fixed selected segment and knot order hold on `-3/7<h<2/5`. | A common centered-control choice `0<h<2/5` is sufficient. |
| B | `T(4+h)=2+h/3`, `T(4-h)=2-h/2`. | Centered slope `5/12`; directional values `1/3,-1/2`; false-centered error `1/12` in the positive direction. |
| C | `q=2,-2,0`, with knot velocity2. | `8/3,1,2`. |
| D | At fixed endpoints the outward target leaves the energy image immediately. | Lower `v=-1` and upper `v=1` must refuse; inward/tangent cases remain in the local domain. |
| E | Both adjacent slopes are2. | The fixed-knot energy coefficient is `1/2`; the interior equal-slope case must not receive a nonsmooth-knot refusal. |
| F | The transformed energies are `(-11,-5,13)`, target4, energy-knot directions `(18,7,37)`, target direction34. | `w=1/2,s'=9`, hence `dT=1/2+(34-22)/9=11/6`. |
| G | `J_z dz=(0,6)`; thermal contribution is `(11/2,-11/3)`. | `df=(11/2,7/3)`. |
| H | On the separately supplied represented ideal branch the slope is `cv*N>0`. | With zero branch motion and unit target direction, `dT=1/(cv*N)`; no new numerical evaluation was performed. |

The nonlinear/kink discrimination comes from the exact formulas rather than a test count or an implementation roundtrip. Synthetic coordinates remain synthetic. Existing saved C7 bytes support the optional derivative-route input identity, not a new physical EOS, thermal history, recipient density, physical uncertainty, or rate derivative.

## Findings at the initial theory checkpoint

No open theory finding. No requested formula, tolerance, physical convention, or input change. No strong no-go admission is proposed; the unequal-slope nondifferentiability statement is a directly proved local property needed for the API.

## Read ledger — initial checkpoint

| Source | Actual scope |
|---|---|
| `unit/THEORY_AND_CONTRACT.md` | Complete, sections1–10, including controlsA–H and frozen API/authority boundary. |
| workflow1.0.0 `references/RESEARCH_POLICY.md` and `EVIDENCE_AND_HANDOFF.md` | Previously read in this native task; reused unchanged. |
| workflow1.0.0 `references/THEORY_LOOP.md` | Complete; R6/R7/R8/R9 boundaries applied. |
| workflow1.0.0 `references/CODING_LOOP.md` | Complete; C5/C6–C8/C9/C10 distinctions applied. |
| `survey/github/PR242/implementation/caloric_branch.py` | Complete actual115-line dependency; exact decoder, constructor domain, evaluate/inverse, supplied-bound behavior. Git blob identity already checked in census. |
| `unit/` file inventory | Names only, to establish when authored source appeared; implementation/test bodies not yet read at this checkpoint. |

The initial verdict is preserved. A single addendum below will record the actual static implementation inspection and any bounded repair closure within this same review pass.

## Single static-code addendum — frozen authored preparation

**Static verdict: PASS_SCOPED_STATIC_PREPARATION. No actual defect requiring author repair was found.** This is the static portion of the requested C9 inspection, not completion of runtime C9 or admission of the coding loop. The initial R6 verdict above is unchanged. The only edits to the initial report at this checkpoint correct Markdown math delimiters and an escaped spacing command; no scientific statement or verdict was revised.

This addendum follows full source reading of the actual new implementation, the seven authored A–G test methods, the verbatim pinned dependency, the future execution wrapper, and the saved-data-only plotting script. It also follows the execution proposal and the prepared identity manifest. No scientific module was imported, no compile or test command was run, and no figure or new numerical result was produced. Read-only SHA-256 checks establish the reviewed bytes, not runtime correctness.

### Implementation correspondence

| Actual source path or function | Independent static assessment |
|---|---|
| `deps/caloric_branch.py` | The constructor requires at least two exact knots, positive first temperature, strictly increasing temperatures and energies, and positive slopes. Its exact decoder rejects floats and booleans. The existing inverse has the stated finite image and supplies the nominal inverse value used by the new API. No dependency change was introduced. |
| `_point` | Checks the closed energy image before `bisect_left`. With the constructor's strict ordering, its returned index is in range, including the final knot. Knot equality is exact and does not introduce an unproved numerical tolerance. |
| `inverse_directional`, open segment | Implements every D1 term with the correct adjacent indices and signs. The nominal inverse value is taken from the pinned branch. The source retains exact rational arithmetic. |
| `inverse_directional`, knots | Selects using `q=v-b[j]`, rather than target direction alone. Outward lower/upper endpoint directions are rejected before accessing an absent segment. The `q=0` path returns the moving knot's temperature direction. The common-linearization flag is true only at an interior equal-slope knot; it is false at endpoints. |
| `inverse_linearization` | Returns the D1 coefficient vectors on an open segment and the common equal-slope knot differential at an interior knot. It issues the distinct named `NonDifferentiableKnot` and `DomainBoundary` refusals required by the contract. |
| `callback_direction` | Performs the supplied matrix/vector product plus the supplied temperature column times the directional temperature. Row/column lengths are checked. `None` has the named missing-input refusal and is never interpreted as a physical zero. |

The code's common-linearization flag does not turn the full finite piecewise-affine inverse into one global Jacobian. It reports local differentiability at the supplied nominal point. The callback wrapper similarly combines supplied derivative data; it does not construct a physical chemical temperature derivative.

### Authored controls and reference independence

The seven test methods implement controls A–G. Their expected values agree with the independent calculations above. Test A compares the moved dependency inverse with a separately written rational curve and verifies the exact forward and centered error expressions. Thus its error reference does not merely compare the new derivative with itself. The chosen positive and negative steps lie inside the declared unchanged-segment domain.

Test B checks both directional signs, rejects the nonexistent common knot differential, and exposes the false centered value `5/12`. C checks all three relative-motion cases. D checks outward/inward/tangent endpoints, endpoint linearization refusal, invalid constructor inputs, exact-type rejection, and direction-vector length. E preserves the differentiable equal-slope knot. F checks the full moving energy-coordinate transformation and detects an inconsistent target transformation. G checks the callback result and missing/malformed derivative inputs.

Control H remains **NOT_RUN_NOT_SELECTED** in the prepared invocation. Its formula was checked manually as part of R6, but no H test body or newly evaluated saved-source result is claimed. Authored A–G assertions are likewise preparation, not seven observed passing tests.

### Execution and presentation preparation

`execution/run_once.py` pins the dependency blob, creates one non-overwriting attempt directory, and prepares one isolated child invocation with the declared 1-second CPU, 10-second wall, and 256 MiB address-space bounds. It preserves child stdout/stderr, source/output identities, exit status, and complete waited-child OS CPU counters. The receipt explicitly excludes wrapper/model/connector/tail costs from that measured scope and preserves unknown costs. The wrapper does not reopen historical reservations or issue stage admission.

`figures/plot_saved.py` reads saved new control data and converts those values only for display. It imports neither the scientific implementation nor the tests. Its proposed two panels correspond to the exact kink counterexample and the smooth finite-difference errors. It packages the figure with saved controls and their numerical receipt, and leaves actual image inspection pending. The proposal supplies external presentation process limits and external accounting; the script's own timing is explicitly a prefix. Neither a figure nor a completed presentation-process receipt exists as evidence in this review.

The future command flag is an invocation convention, not a new resource grant. The proposal correctly remains **NOT_APPROVED / NOT_RUN**. No historical planning, presentation, or main-budget allowance was transferred or reset in this pass.

### Read and identity ledger — static addendum

All paths below are relative to `/workspace/scratch/cc0531120bc9/rei_loop_continuation_20261028/unit/`. Each listed source was read in full. The six SHA-256 values were independently obtained by the reviewer with read-only `sha256sum` and match `execution/PREPARED_IDENTITIES.json`.

| Source | SHA-256 of reviewed bytes |
|---|---|
| `THEORY_AND_CONTRACT.md` | `92e067c1cd6cc81cddbd1bd1e91fbc5025ea78914f041db69f42fe7ead2f5758` |
| `deps/caloric_branch.py` | `ac5e5d50a454185550ba5614e50e914b7dad613795cf743347bd8b0b41c61aef` |
| `implementation/directional_pullback.py` | `13f26afa9ecbfa367609f0391367ca11c0a9991154c02a6d6ba19d9add1ff753` |
| `tests/test_directional_pullback.py` | `336b3d9dabbe21d42f9797cb1566c98a08fbe397ea66d6f856ef787f0accfd4f` |
| `execution/run_once.py` | `a3f25b697171a15929a906a25037a647202d85407bf4611daaec37861c3c3c52` |
| `figures/plot_saved.py` | `4a3f94682d7ed809e2ccfc0d8f87b2a2f2304c5155be672ee3e299d73f28a4b6` |

Additional complete reads: `execution/EXECUTION_PROPOSAL.md` and `execution/PREPARED_IDENTITIES.json`. The dependency is the earlier verified Git blob `bc3ebd682c363afc7d5c36d164406086145b6964` at PR242 head `3f299062a0d0d35c17f83a9e6081ca515e9d4c4c`; matching current SHA-256 bytes preserve that identity.

### Closure and exact remaining scope

| Review/stage item | Status after this single pass |
|---|---|
| R6 independent mathematical review | **PASS_SCOPED_INDEPENDENT_THEORY** |
| C9 actual-code static preparation inspection | **PASS_SCOPED_STATIC_PREPARATION** |
| C6–C8 execution, results, and figure validation | **NOT_RUN** |
| Runtime C9 / complete coding-loop admission | **NOT_COMPLETE** |
| Optional saved-source H execution | **NOT_RUN_NOT_SELECTED** |
| New physical EOS, callback `F_T`, recipient temperatures/radii, or global readiness | **NOT_ESTABLISHED** |
| Canonical counters, accepted dependency edges, or stage admission mutations by this reviewer | **NONE** |

There is no requested author repair and no recursive or replacement reviewer. A future authorized run still needs its actual exit/output/accounting evidence and, if presentation is authorized, an actual image read before the corresponding runtime and presentation stages can be accepted. This review establishes the scoped theory and authored static preparation only.

