# R6 phase one: independent source-only review

Unit: `rei_rr_mao_finite_temperature_enclosure_20261028`  
Reviewer task identity: `/root/rr_mao_native_reviewer`  
Author task identity stated in the submitted proof: `/root`  
Phase-one review date: 2026-10-28 UTC  
First explicit clock observation: 12:26:47 UTC; pre-report clock observation: 12:29:38 UTC.

## Provisional conclusion

The submitted derivation is mathematically adequate for the scoped represented-real RR/Mao functions, conditional on the stated inclusion-preserving interval primitives being implemented with finite outward bounds. I found no source-algebra counterexample and no correction needed to RR0–RR6, M0–M3, L0–L2, or T0–T1. In particular, the lithium temperature correction is differentiated, the selected Mao factor retains its squared-log and numerator terms, and the two-sided log-temperature Taylor statement follows with the same uniform second-derivative bound.

This is an R6 source-only judgment. It does not establish that a numerical implementation exists, implements the contract, or has been validated. C9 has not been performed by this reviewer. Arithmetic context bounds, executable primitive guarantees, returned interval records, input refusal behavior, caching behavior, numerical containment, and saved-data plotting remain unreviewed. Test counts, other reviewers' verdicts, and project admission counts were not used to determine this conclusion.

## 1. Independence, host identity, and exposure boundary

The actual task identifier supplied to this agent is `/root/rr_mao_native_reviewer`. The assignment arrived as a new task with no inherited parent conversation visible in this agent's context. The assignment stated that `fork_turns='none'` was used; I did not inspect the parent's spawn record. No opaque process identifier or hardware isolation attestation was available to me.

Mechanical host observations returned:

- Working directory: `/workspace/scratch/cc0531120bc9`.
- Hostname: `0e9a46d15332`.
- Kernel/platform from `uname -srm`: `Linux 6.18.55 x86_64`.

This is an independent review task on a shared filesystem, not a security-enforced blind environment. I could in principle have opened adjacent files. I deliberately did not read sibling reviews, status/handoff documents, census files, new implementation files, test source, CAS output, or raw numerical results of this unit. The supplied author proof itself contains contextual status and proposed controls, and the original selected Mao JSON contains historical numerical evaluations. Those exposures are recorded explicitly below and in the separate read ledger. They cannot be represented as total blindness to author expectations or historical source evaluations.

The defining source files were read as text. No Python source was imported or executed. No scientific program, CAS, test, oracle, plotting program, or external write was run. Mechanical commands were restricted to text reading, source-key selection, file identity/size inspection, host identity, clock observation, and writing this report and its ledger. Tool, model, scheduling, token, host, and storage overhead is unmeasured and is not asserted to be zero.

The precise read/exposure ledger is `R6_PHASE1_READ_LEDGER.md` in this directory. The report and ledger are to be hashed before any lateral implementation or result evidence is read. Later review must be an append-only follow-up artifact; it must not silently replace this phase-one conclusion.

## 2. Source identity and the actual selected closure

### 2.1 Coefficients and exact-real semantics

The inspected coefficient file is:

`/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/unit/source/atomic_coefficients.json`

Its mechanically observed SHA256 is `38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc`, and `git hash-object` returned blob `2eba600a9d7a7359ca55f566f1b841a363a3e5c7`, matching the assignment and the author proof. The six RR rows in the proof agree with this JSON's `rr` object. Its runtime domain is `[100.0, 1000000.0]` K.

The submitted theorem explicitly takes the exact real image of the binary64-decoded coefficients and of `1e-6`, `1.380649e-23`, and `1.602176634e-19`. This is a legitimate differentiable real function. It is not a theorem about all intermediate rounding operations in NumPy/Python. The source does contain floating arithmetic, but the author has explicitly defined the representation level at which the theorem applies. I found no covert substitution of nominal decimal coefficients for that declared real-image convention in the derivation.

The stipulated PR237 commit is `ee6746ab172f862dddfdec63b59e5e3707b59eaa`, provided in the assignment and author text. I did not independently fetch or validate the remote Git commit, nor inspect the PR241 or VigilODE dependencies. The verified local byte identities support the local mathematical source review; they do not independently establish the remote commit history.

### 2.2 RR and Mao source definitions

In `source/recombination_moments.py`, the definitions at lines 102–120 give `z=T2/T`, the exponential correction, the effective exponent, `u`, `v`, alpha, its logarithmic slope, and the logarithmic slope derivative. They agree with RR0–RR3 after identifying `du=p/2`, `dv=q/2`, `ddu=p(1-p)/4`, and `ddv=q(1-q)/4`.

In `source/thermal_sources.py`, `mao_factor` at lines 22–33 uses `t=T*KB_J_K/EV_J`, `np.log(t)`, the full `-b0*lt-c0*lt**2` exponent, and `(1+v)/(1+u)`. This is M0. Its returned derivative is `f*m_1` with exactly the signs in M1.

The constructor at line 45 defaults to `rr_closure='mao2017'`. Lines 67–77 replace the RR loss by `KB_J_K*T*alpha*f` and its first logarithmic derivative by `KB_J_K*T*((alpha+Dalpha)*f+alpha*Df)`. Thus L0 and L1 describe the selected native closure at the stated represented-real level. The alternative rate-derivative closure remains a distinct branch. Binding-energy escape is handled separately at line 101 and is not a term in this RR kinetic-loss coefficient.

### 2.3 Selected Mao rows and preserved original lock

The supplied selected JSON SHA256 is `34b5fb8dab049744faa0c6f734ce59f1c72b931b3cf2db298c01156f86d17803`. I first attempted to read the lock at the literal location implied by the relocated `thermal_sources.py`, namely `unit/provenance/MAO_SOURCE_LOCK.json`; that file was absent. The parent then supplied a source-only preserved location:

`/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/survey/physics/source/MAO_SOURCE_LOCK.json`

I read this original lock in full. Its selected-file SHA256 equals the supplied selected JSON SHA256. The preserved raw `pars.dat` and `calc.dat` also match both their locked byte lengths and SHA256 values. The lock's own SHA256 is `09257023bc18bc01133389aad3a9796e9dc2bfbc59c643ca9659e849776931b0`.

The six relevant raw parameter-table rows agree visually with the selected JSON under `n=Z-q+1`:

| RR key `(Z:q)` | Recombined electron count `n` | Raw `mao2017_pars.dat` line |
|---|---:|---:|
| `1:1` | 1 | 1 |
| `2:1` | 2 | 31 |
| `2:2` | 1 | 2 |
| `3:1` | 3 | 60 |
| `3:2` | 2 | 32 |
| `3:3` | 1 | 3 |

In particular, the actual `3:1` parameter row has `c0=0.007567`, and both `2:1` and `3:1` have nonzero `a2`. No simplification removes those terms. I did not recompute the historical table comparisons or the values at 12000 K.

The initial missing literal lock path is therefore resolved as an available preserved provenance input for this source-only review. I did not reconstruct a runnable native directory or establish that its loader can open the relocated paths. That filesystem/runtime question is separate from the now-identified selected mathematical function.

## 3. Independent mathematical audit

### 3.1 RR differentiation

Let `x=ln T`, so `d/dx=D`. Then `Du=u/2`, `Dv=v/2`, and `Dz=-z`. For `b=B+C exp(-z)`, direct product differentiation gives

`Db=C z exp(-z)` and `D²b=C z(z-1)exp(-z)`.

Writing `F=ln(alpha/(sA))` gives

`F=-ln u-(1-b)ln(1+u)-(1+b)ln(1+v)`.

Its first derivative is exactly RR2. In the second derivative, the exponent-dependent bracket contributes `b_1(p-q)/2`, and differentiating `b_1*lambda` contributes another `b_1(p-q)/2` plus `b_2*lambda`. Their sum is `b_1(p-q)`, as in RR3. The remaining terms use `Dp=p(1-p)/2` and `Dq=q(1-q)/2`. Therefore RR3 has the correct full coefficient and signs.

The ordinary exponential differentiation identities then give `Dalpha=alpha*r_1` and `D²alpha=alpha*(r_1²+r_2)`. This agrees with the native source's slope and curvature definitions. No third derivative is required for this RR second derivative or the selected Mao loss second derivative.

### 3.2 Actual-row strict decrease

All six supplied RR rows have `A>0`, `T1>T0>0`, `T2>=0`, `C>=0`, and `0<B<=b<=B+C<1`. The margins from zero and one are far larger than binary64 rounding discrepancies. Consequently `p,q>0`, and the negative bracket in RR2 is strictly negative.

For `T1>T0`, `u>v>0`, so `lambda>0`. The inequality `(1+u)/(1+v)<u/v` gives `lambda<(1/2)ln(T1/T0)`. Since `z exp(-z)<=1/e` for `z>=0`, the positive correction to the logarithmic slope is at most the quantity used in RR5. Hence `C ln(T1/T0)<e` is sufficient for strict decrease on all `T>0`.

The author's rational witnesses for the two nonzero-C rows are valid. In `3:1`, `C<151/1000` and `T1/T0<2^16`; in `3:2`, `C<36/1000` and `T1/T0<2^18`. The latter ratio can also be certified with the still weaker source-image bound `T0>34`, since `34*2^18>7329000`. Together with `ln 2<7/10` and `e>27/10`, both yield strict margins. The displayed positive-series proofs of those elementary logarithm/exponential comparisons are valid.

It follows that the actual six rows are strictly decreasing. Continuity then gives the exact range `[alpha(Tb),alpha(Ta)]` for every contracted interval, including singleton intervals. No monotonicity of `f` or `L` is required or inferred.

### 3.3 Mao derivatives and positive source function

Because `ell=ln(kT/eV_J)`, `Dell=1`. For `U=a1 exp(-b1 ell)` and `V=a2 exp(-b2 ell)`, the logistic derivatives are `DP=-b1 P(1-P)` and `DQ=-b2 Q(1-Q)`.

Differentiating `ln(f/a0)=-b0 ell-c0 ell²+ln(1+V)-ln(1+U)` gives M1. A second derivative gives the positive `+b2² Q(1-Q)` contribution and negative `-b1² P(1-P)` contribution in M2, together with `-2c0`. These signs and the squared-log curvature term are correct.

Every selected row has positive `a0` and nonnegative `a1,a2`. Thus `1+U` and `1+V` are strictly positive for positive T. The zero-a2 rows cause no singularity: `V=Q=0` and their terms vanish without taking `ln(a2)`. M0 is smooth and strictly positive throughout an open neighborhood of the contracted domain. The natural-log convention and Kelvin-to-numerical-eV conversion match the defining native source.

### 3.4 Loss derivatives and interval construction

For `L=kT alpha f`, logarithmic differentiation gives `Dln L=1+r_1+m_1`. The leading `1` comes from the factor T. Differentiating once more gives `D²L=L*((1+r_1+m_1)²+r_2+m_2)`, exactly L2. Every multiplicative factor in L0 is positive, so L is strictly positive on the domain.

On a closed interval inside `[100,1000000]`, every argument supplied to sqrt, log, positive real power, exponential, and division in the proof is finite and lies in the appropriate mathematical domain. The real denominators `u`, `1+u`, `1+v`, `1+U`, and `1+V` are bounded away from zero. Consequently finite interval extensions can be formed for the displayed expressions and for both second derivatives. Using outward images of alpha's monotone endpoints sharpens the alpha range without assuming any behavior of f or L.

Natural interval dependency can widen the boxes substantially. It does not invalidate inclusion. For example, a computed interval expression for `P(1-P)` may be much wider than its pointwise range; the proof only needs inclusion. Squared logarithms must be enclosed with valid interval arithmetic when their arguments cross zero. No endpoint-only extremum argument for f or L is present in the submitted proof.

The phrase “strictly positive lower endpoint when representable” correctly distinguishes mathematical positivity from a finite-format rounding guarantee. For executable acceptance, the chosen arithmetic contexts must actually supply finite outward bounds and either preserve the required positive denominator bounds or refuse an unsupported context. No finite-context claim is established here by compactness alone. The author already assigns explicit primitive rounding and context obligations to the coding stage.

### 3.5 Uniform two-sided log-temperature remainder

For any admitted anchor and target in the same positive interval, set `h=ln(Ttarget/Tstar)`. The path `Tstar*exp(th)` for `0<=t<=1` stays between its endpoints, so it stays in I. An equivalent exact integral remainder is

`y(Ttarget)-y(Tstar)-Dy(Tstar)*h = h² ∫_0^1 (1-t) D²y(Tstar exp(th)) dt`.

This formula holds for positive, negative, and zero h. If the interval construction supplies `|D²y|<=B2_y` throughout I, taking absolute values immediately gives `B2_y*h²/2`. The second-derivative bound is uniform over every anchor/target pair in I; it is not a sample-based inference.

If outward intervals Y0, Y1, and H contain the exact base value, derivative, and h, then interval addition and multiplication place the linear part in `Y0+Y1*H`. Since `|h|<=max(|H.lo|,|H.hi|)`, the rounded-up radius in T1 encloses the analytic remainder. Thus the final result correctly includes arithmetic uncertainty. An exact equality of encoded anchor and target justifies the exact zero-step branch `H=[0,0]`, `rho=0`, and final enclosure Y0.

The manufactured coalescent-scale and equal-Mao-ratio controls in the proof are also algebraically consistent. They are declared analytic controls, not changes to the actual coefficient rows or actual domain. No executed-control result is inferred from them.

## 4. Findings and disposition

| ID | Equation/source location | Observation and effect on scoped claim | Counterexample | Minimal repair or scope action |
|---|---|---|---|---|
| R6-P1 | RR0–RR6; `recombination_moments.py` definitions of alpha, slope, curvature | Differentiation, positive source assumptions, and strict actual-row monotonicity are supported. Endpoint alpha range follows. | None found in the analytic/source review. | No equation repair required. Retain exact binary64-image semantics. |
| R6-P2 | M0–M3 and L0–L2; `thermal_sources.py` `mao_factor`, constructor, coefficients | Selected natural-log Mao hybrid, row mapping, numerator term, c0 term, and T-factor derivatives are consistent. | None found in the analytic/source review. | Preserve the selected source and distinguish the alternate closure. |
| R6-P3 | Section 5 interval construction and B0; section 8 executable obligations | Mathematical interval construction is valid conditional on finite inclusion-preserving primitives. An executable guarantee is not established by this source-only phase. | No implementation was available for review; no implementation counterexample is asserted. | C9 must inspect actual primitives, contexts, source conversion, and returned bounds; no R6 verdict substitutes for that work. |
| R6-P4 | T0–T1 | Uniform continuum remainder is valid for both signs of h, with full arithmetic uncertainty and exact zero-step handling. | None found in the analytic/source review. | No theorem repair required; executable arithmetic remains pending. |
| R6-P5 | `thermal_sources.py` loader; preserved original Mao lock | Literal relocated lock path was absent; the subsequently supplied preserved original lock resolves selected source byte identity. Standalone runtime layout was not verified. | Missing path is a reproduced mechanical observation, not a mathematical function counterexample. | Keep the preserved source identity and location reconciliation explicit; validate runtime layout only if claiming a runnable native reconstruction. |
| R6-P6 | R5 sections 1 and 8; source historical comparisons | Fitted residuals and closure differences are not uncertainty enclosures for derivatives, hybrid loss, or physical state. The proof already respects that scope. | No expanded physical claim is established or tested. | Retain the stated null physical-temperature/state/radius scope and separate later physical certification. |

There is no identified fatal mathematical defect requiring the author to revise the scoped theorem before proceeding. That conclusion is based on the equations and supplied defining sources. It does not depend on a favorable check count or an expected review verdict.

## 5. Sources not independently established and remaining limits

The Badnell and Verner author pages and Mao2017 DOI were named in the assignment/proof. I did not retrieve their web pages or the publication during this phase. The present claim concerns the fixed supplied functions, for which the defining native code, selected coefficient table, and preserved source lock were sufficient. Independent validation of physical fit accuracy, publication interpretation beyond these source encodings, or remote commit ancestry is not claimed.

The author manuscript's statements about prior DR acceptance, current remote-tip census, original DAG counts, PR241/VigilODE status, and pending figure/resource obligations were read because the full unredacted manuscript was required. They were not investigated or adopted as findings. The historical Mao comparison and `f_at12000` numbers are original-source exposure, not fresh results produced by this unit or by this reviewer.

No IVP, actual recipient temperature, native state, physical radius, empirical fitting-error certificate, or global physical-completion determination was reviewed. The phase-one conclusion is restricted to the represented-real six-row functions and their constructive finite-interval and finite-log-step mathematics.

## 6. Phase-one preservation statement

At the time this file and its read ledger were first written, no new implementation source, test source, CAS output, direct-oracle output, raw numerical record, saved figure, sibling review, or handoff/census artifact had been inspected. Before that first write, the only parent follow-up supplied the location of an original source lock and its original source tables. After the first write and before hashing, the parent announced that implementation source was ready and supplied its path and hash plus the inherited arithmetic path and hash. No code contents or new test/CAS/result contents were supplied or read before sealing. This metadata exposure and its order are recorded in the ledger; the mathematical conclusion was already written.

Hashing these phase-one artifacts preserves a concrete provisional record. It does not provide security isolation from the shared filesystem. Any later C9 or other evidence must be identified by a new review stage and must retain this initial record.
