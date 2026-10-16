# Nonlinear residual and adaptive-error diagnostic budget

## R1 — position and scope

This unit constructs a deterministic diagnostic that maps an actual four-component backward-Euler residual and Jacobian into the coordinate scaling used by the existing adaptive comparison. It reports a linearized Newton correction, conditioning and linear-system backward error. Missing stage residual/Jacobian data yields HOLD for actual-stage attribution. Production source005, the active source009 runner, their tolerances and their states are unchanged.

Read-only GitHub intake is pinned at `fdfda0fec423ccb7175552c7dc066be93ce347e1`; exact blob identities and inspected source excerpts are in `evidence/SOURCE_PIN.json` and `evidence/SOURCE_EXCERPTS.txt`. The current `ResidualContext.evaluate` orders unknowns as `(x_HII,x_HeII,x_HeIII,w_eV_per_H)` and evaluates `R=y-y_old-dt*f(y)`, with prepared absorption fixed throughout each chemical-stage Newton solve. The existing termination threshold is 1e-11 in its own residual scaling, and the adaptive target is 1e-5 in a different state scaling.

The source007 independent review observed larger temperature differences after refinement, accepted-stage maximum Newton residuals near 9e-17 for h/2 and 7.36e-12 or 9.05e-12 for h/4, and nonidentical actual endpoint bits. It identified nonlinear termination as a supported confounder, without proving its contribution. The saved maximum alone does not identify a residual vector, a Jacobian, a stage or a linearized state correction. The new diagnostic fills that explicit computation and input contract, with synthetic fixtures testing its mathematics independently of the active runner.

The existing full005 PL result at commit `0c3958d11d654513eb23cf462d5148e87ba6c9de` is reused: saved-PL Tgas supremum 0.24946455408644397 K and RMS 0.1128202745602529 K. Its postprocessing cumulative debit 156.5376037069618 s of 300 s and original deadline remain its own retained allocation. No PL check, solver campaign or full-data reduction is repeated here.

Completion requires a derived scale transformation, an explicit distinction between residual and state error, a backward-Euler full/half-step example, independent algebra/fixture checks, and a standard-library implementation contract accepting actual stage packets. This unit may create only new files under `research/flrw_nonlinear_error_budget_20261016/`; no production Rust or canonical campaign file is mutated. Actual-stage diagnosis remains NOT_RUN until a correctly identified packet is supplied by its owner.

## R2 — source and literature mapping

The pinned code gives four directly used facts. `ResidualContext.evaluate` (driver lines 256–287) evaluates a backward-Euler chemical residual with active photon absorption computed from the candidate gas and fixed prepared quadrature. `Driver::norm` (792–798) leaves the three fraction residuals unscaled and divides the energy residual by `max(|w_old|,|w|,1e-6)`. `chemical_stage` (831–834) accepts this norm at 1e-11. `error_metric` (973–981) instead divides each fraction difference by `max(|x_half|,1e-5)` and energy difference by `max(|w_half|,1e-6)`. Photon-number and photon-energy comparisons are additional components of the production adaptive metric; this unit's four-variable correction addresses the chemical block only.

`igm_state.rs` defines `w=(3/2) k_B T (1+f_He+x_HII+f_He(x_HeII+2x_HeIII))` per H nucleus. It also makes the adiabatic map exact at fixed fractions. These definitions determine the thermal projection used below, without adding an independent energy owner. The source007 review is reused as an actual observation of unresolved mixed truncation/termination effects. Source009's independent review authorizes two short runs after implementation checks; its decision label alone is not evidence that those histories finished.

On 2026-10-16 the controller used Exa to retrieve the official [CVODE mathematics description, §3.2.1.1](https://sundials.readthedocs.io/en/latest/cvode/Mathematics_link.html). It ties nonlinear stopping to the local error test in a weighted norm. That supports the question of matching residual/correction scales, while the current REI solver uses its own max norm and algorithm. The unit does not adopt CVODE constants, convergence results or its WRMS norm. SciSpace returned Enright and Seward (1989), DOI `10.1007/BF02243229`, and Rodrigues (2017), arXiv `1705.04870`, as contextual leads; discovery abstracts provide no premise for the derivations here. Primary Wolfram double-step documentation supplies method context. Only compact search metadata are published, not source page text.

Root's independently executed backward-Euler algebra is available for R6. Its earlier midpoint toy is not the production chemical-stage method and is excluded from this unit's supporting derivation. The required math below uses elementary matrix scaling, a Taylor expansion with explicit conditions, and the scalar backward-Euler map, so no unverified literature lemma is needed.

## R3 — definitions, assumptions and observable map

Let `y=(x_HII,x_HeII,x_HeIII,w)` be one accepted chemical-stage iterate in units `(1,1,1,eV/H)`. Let `y_old` be that stage's old gas state, `R=R(y)` the unnormalized four-vector and `J=dR/dy` or an explicitly labeled finite-difference approximation evaluated at exactly the same iterate and prepared-absorption context. The point, stage duration, input identity, Jacobian construction and added evaluation cost must be retained. The production solver accepts `||R||_N <= 1e-11` before forming a Jacobian; therefore an accepted-iterate J is not already stored, may require new charged evaluations, and cannot be substituted by the last iteration's J. A packet lacking R/J or binding them to different states/contexts yields HOLD for actual-stage analysis.

Freeze positive diagonal scales at the supplied iterate:

`S_R = diag(1,1,1,max(|w_old|,|w|,1e-6))`,

`S_y = diag(max(|x_HII|,1e-5),max(|x_HeII|,1e-5),max(|x_HeIII|,1e-5),max(|w|,1e-6))`.

Define `b=S_R^-1 R`, `A=S_R^-1 J S_y`, solve `A z=-b`, and set `delta=S_y z`. These scales are evaluated once; A is not the derivative of the state-dependent normalized residual. The diagnostic residual is `||b||_infinity`, the linearized correction in adaptive chemical coordinates is `||z||_infinity`, and its ratio to the unchanged 1e-5 target is reported descriptively. This ratio does not authorize rejection, a new tolerance or a physical error bound.

For nonsingular A, report `kappa_infinity(A)=||A||_infinity ||A^-1||_infinity` and the computed linear-system normwise backward error `eta=||A z+b||_infinity/(||A||_infinity ||z||_infinity+||b||_infinity)`, with eta=0 when all numerator/denominator terms vanish. A singular matrix has no unique correction and returns typed HOLD; nonfinite input/arithmetic also returns HOLD rather than Infinity or NaN. Finite ill-conditioning is reported, with no arbitrary condition-number acceptance threshold. A computed inverse and backward error are binary64 diagnostics, not certified interval bounds.

For thermal projection let `f=f_He=nHe/nH`, `D=1+f+x_HII+f(x_HeII+2x_HeIII)` and `k=k_B` in eV/K. Then `T(y)=2w/(3kD)`. The linear correction is `deltaT_linear = T*(delta_w/w - delta_D/D)`, where `delta_D=delta_xHII+f*(delta_xHeII+2delta_xHeIII)`. If the corrected fractions satisfy `0<=x_HII<=1`, nonnegative HeII/HeIII with sum<=1, and corrected w>0, also report `T(y+delta)-T(y)` using the exact EOS map; otherwise return a null exact thermal projection with an explicit corrected-state-domain reason. No clipping or state commit occurs. This map evaluates a Newton correction at the chemical stage before the final geometry map; propagation through the split step, photons or subsequent evolution requires separate information.

The actual-stage claim is conditional on the supplied packet. The planned mathematical fixtures are explicitly synthetic; they do not identify which residual component caused the source007 temperature pattern. The original production acceptance inequalities remain distinct: Newton uses `<=1e-11`, while adaptive acceptance uses `<local_target` and `<2e-4`.

## R4 — discriminating alternatives

Three candidate actions were compared. A threshold-partition quadrature study targets source008's changed GammaHI/photon representation, but that separate change cannot isolate source007 nonlinear termination. Lowering the production Newton threshold would alter a frozen solver before measuring the contribution. A read-only scaled residual/Jacobian diagnostic directly identifies the missing local information and can be implemented without changing either active source. Select this third action.

A raw residual norm alone misses two distinct effects. First, for a neutral helium coordinate the production stopping scale is 1, whereas the adaptive chemical scale is 1e-5; a residual 1e-11 corresponds to 1e-6 in that coordinate's adaptive residual scaling even with an identity Jacobian. Second, inversion can amplify or suppress the residual: with `J=diag(1e-8,1,1,1)`, `R=(1e-11,0,0,0)` and x_HII=1/5000, the correction is delta_xHII=-1e-3 and its scaled magnitude is 5. The latter is an explicit affine-system example, not a measured REI Jacobian. Its corrected hydrogen fraction is outside the physical domain; the diagnostic must report that fact instead of clipping or applying the correction.

Step doubling adds a separate possible cancellation. For scalar `y'=-lambda*y`, backward Euler has q=1/(1+z) and a half step has qh=1/(1+z/2), z=lambda*h. The fine/coarse difference contains both `(qh^2-q)y0` and propagated equation residuals. A synthetic residual chosen within 1e-11 can cancel the observed pair difference while the fine trajectory differs from the exact exponential. R5 derives this explicitly. This scalar construction demonstrates an estimator mechanism; it does not assign the order of the production split method or explain the observed source007 difference without its missing stage data.

Thermal projection adds practical interpretation: the same correction norm can act on energy, ionization or both, and composition changes alter particle count in the EOS. A valid fixture with proportional changes in w and particle factor D will have zero temperature change despite nonzero state corrections. This separates a thermal observable from the vector norm without adding an evolution model.

The selected implementation therefore returns raw/scaled residuals, scaled linearized correction, conditioning, backward error and conditional thermal projections. It consumes a stage packet, rather than reconstructing unavailable information from a run-wide maximum. The first mathematical tests exercise scale mismatch, inversion, cancellation and valid/invalid thermal projections; none requires a native runner or a repeat of the PL study.

## R5 — constructive derivation and frozen probe

**Scale equivalence.** Multiplying `J delta=-R` by `S_R^-1` and substituting `delta=S_y z` gives `A z=-b` exactly. Positive diagonal scales are invertible, so the two linear systems have the same unique correction whenever J is nonsingular. The actual infinity norms are max absolute vector entries and max absolute row sums for matrices. In exact arithmetic `||z|| <= ||A^-1|| ||b||`; this is a bound on the linear-system solution under the supplied J, not on the nonlinear root error. In binary64 the returned inverse/norm/backward error are estimates and no certified bound is emitted.

For a change of energy unit by u>0 let `P=diag(1,1,1,u)`. Transform `y'=Py`, `R'=PR`, `J'=PJP^-1`, and both scale matrices by `S_R'=PS_R`, `S_y'=PS_y`, including the energy floors. Then `A'=A`, `b'=b`, `z'=z` and `delta'=P delta`. Thus the scaled diagnostics are unchanged by consistent energy-unit conversion. The production packet adapter remains eV/H; this identity is exercised by the generic scaled-system core and the independent probe.

**Residual bridge and missing nonlinear hypotheses.** The native acceptance condition gives `||S_y^-1 R|| <= ||S_y^-1 S_R|| * 1e-11`. The diagonal gain is `max(1/s_HII,1/s_HeII,1/s_HeIII,s_Rw/s_yw)`. When a species uses the 1e-5 floor, its residual-scale allowance is 1e-6. The thermal ratio depends on old/current w and is retained explicitly; it is not replaced by one in general. State correction further requires the inverse Jacobian. The norm or condition number alone neither diagnoses stiffness nor establishes a physical error.

If an exact root y_star exists, the segment to it lies in a differentiability domain, and the averaged Jacobian `Jbar=integral_0^1 R'(y+t(y_star-y))dt` is invertible, the fundamental theorem gives `y_star-y=-Jbar^-1 R(y)`. The computed correction uses J at y (or a labeled finite-difference approximation) instead. A quantitative nonlinear remainder bound would need additional neighborhood derivative/inverse information. The stage packet has no such witness, so the implementation reports a linearized correction and does not infer a true root-error bound. The distinction remains relevant at species-domain boundaries and with the production one-sided finite-difference fallback.

**Backward-Euler estimator mechanism.** For `y'=-lambda*y`, z=lambda*h>=0, define q=1/(1+z), qh=1/(1+z/2). If the full and half-step equation residuals are rF,rA,rB with convention `(1+z)y_new-y_old=r`, then

`yhat_F=q(y0+rF)`, `yhat_A=qh(y0+rA)`, `yhat_B=qh(yhat_A+rB)`.

Therefore

`yhat_B-yhat_F=(qh^2-q)y0 + qh^2*rA + qh*rB - q*rF`,

`qh^2-q = -z^2/((1+z)(2+z)^2)`.

The exact pair signal is order z^2 with leading term `-z^2/4`. A tolerance independent of this signal can cancel it. For z=1/200000, y0=1, rA=rB=0, choose `rF=(1+z)(qh^2-q)=-1/160000800001`. Its magnitude is below 1e-11 and the computed pair difference is exactly zero, while the fine value qh^2 differs from exp(-z). This proves the stated synthetic cancellation, with no claim about the order or realized errors of the production geometry/source/chemistry splitting. The source007 endpoint offsets and nonlinear contributions remain separate unmeasured terms.

**Thermal correction.** With c=2/(3k), D as in R3 and dD its correction,

`DeltaT_EOS = c*(D*delta_w-w*dD)/(D*(D+dD))`,

`deltaT_linear = c*(delta_w/D-w*dD/D^2)`,

`DeltaT_EOS = deltaT_linear/(1+dD/D)` and `DeltaT_EOS-deltaT_linear = -dD/(D+dD)*deltaT_linear`.

These avoid subtracting nearly equal absolute temperatures. They are exact algebraic identities for a proposed correction; binary64 evaluations remain rounded. A positive D+dD alone does not ensure physical ionic fractions, so the corrected-state domain check precedes the exact EOS projection. The linear directional projection can still be reported when the full proposed correction leaves that domain, with the exact projection null and the reason explicit. If `delta_w/w=dD/D`, both thermal changes vanish although the vector correction can be nonzero.

**Frozen independent probe.** `FIXTURE_SPEC.json` fixes eight exact-rational constructions: identity and coupled matrices, species-floor bridge, a large-inverse example, singular rejection, energy-unit transformation, valid EOS cancellation, and scalar BE cancellation. The synthetic thermal constant k=1/10000 eV/K is deliberately a positive rational fixture constant, not a physical CODATA substitution. The oracle uses exact rational elimination and inverse calculations independent of the later production implementation; finite binary64 comparisons use test-local relative 1e-12 and absolute 1e-14, with exact equalities wherever rational. Those tolerances judge fixture arithmetic and are not scientific acceptance criteria. The singular construction is expected to return a unique-correction HOLD. Probe work is confined to the new unit's probe directory, one initial execution and at most one diagnosed repair execution, each with a 30 s cap, zero native builds/solves and zero physical-history reads. It starts only after R5 immutable capture and records its actual resources and outputs.

R5 completes the conditional matrix/thermal derivations and explicit cancellation construction. R6/R7 still require independent symbolic/fixture evidence before implementation adoption. Current production R/J telemetry remains unavailable and no actual-stage result is inferred from the completed mathematics.

## R6 — independent theory verification

The fresh read-only reviewer returned `PASS_SCOPED_THEORY` in `evidence/R6_INDEPENDENT_REVIEW.json`, with no findings or required correction. It independently checked the matrix-scaling sign/equivalence, frozen scales, inverse-norm/backward-error interpretation, missing accepted-state Jacobian, scalar BE contamination/cancellation, EOS algebra/domains and all eight fixture designs. It used the pinned driver excerpts and a blob-verified EOS file; the different local driver snapshot was explicitly excluded. The reviewer ran no symbolic, numerical, native or probe computation, so this is independent argument/source review, not an extra execution claim.

Three actual root Wolfram responses are retained under `evidence/intake/`. `WOLFRAM_INEXACT_BE.json` verifies `qh^2-q=-z^2/((1+z)(2+z)^2)` with zero identity residual, its expansion and the residual-contamination expression. `WOLFRAM_ESTIMATOR_CANCELLATION.json` returns the exact rational `rF=-1/160000800001`, verifies its magnitude is within 1e-11, returns exactly zero observed pair difference, and evaluates the constructed fine-versus-exponential error as approximately 6.24995833350260360677e-12. `WOLFRAM_EOS_CORRECTION.json` returns zero for both the exact-minus-linear identity and the directional-derivative identity. These checks support the stated scalar/thermal formulas and do not supply actual REI residual data.

Additional `evidence/R6_SOURCE_EXCERPTS.txt` shows the production return before Jacobian formation and the EOS particle/energy relation from the same pinned blobs. This closes the source-intake gap without editing a production file or rerunning a completed campaign. R6 accepts the formulas and fixture design within their conditional scope; actual fixture execution is separately assessed in R7.

## R7 — independent small-case execution

The separate probe worker executed the frozen eight-case contract using exact Fraction elimination/inversion and an 80-digit Decimal exponential for the scalar illustration. The source, full results and both execution logs are under `probe/`; `probe/EXECUTIONS.json` records the actual commands and outcomes. The theory owner read the script, result and logs; no completed probe was replayed.

The species-floor fixture yields native residual norm 1e-11, scaled correction norm 1e-6 and target ratio 1/10. The large-inverse fixture has the same native residual norm but delta_xHII=-1/1000, scaled correction norm 5 and scaled condition number 5e11. Its corrected hydrogen fraction is -1/1250, so the exact thermal projection is null while the linear projection remains defined. The valid EOS cancellation has a nonzero correction norm 1/20, unchanged temperature 500/99 K, and exact/linear temperature changes both zero. Consistent energy-unit conversion leaves A,b,z,conditioning and thermal outputs exactly unchanged. The singular fixture returns a HOLD with null correction/condition result.

The exact scalar BE pair signal is `-200000/32000320001000001`, while the residual-contaminated pair signal is exactly zero with `rF=-1/160000800001`. The 80-digit exponential check gives a nonzero fine-state error approximately 6.24995833350260360677e-12. These are synthetic consequences of the explicit input equations, not an inference about an unrecorded production stage.

The first execution exited 1 because the probe loader treated the `base_residual` alias in the singular fixture as individual characters. The worker preserved `stdout_initial.log`, fixed that single loader error without changing a formula or fixture, and used the one permitted repair execution. The second execution exited 0 with `PASS_SCOPED_EIGHT_SYNTHETIC_CASES`, CPU 0.0035221950000000023 s, wall 0.003524641004332807 s and peak RSS 10880 KiB. Initial internal timing was not recorded and remains null. No probe executions remain under this small allowance. There were zero production-module imports, native builds/solves, physical-history reads or PL reruns. This closes the mathematical fixture obligation; the forthcoming implementation has its own targeted checks against these cached independent results.
