# Moving-knot caloric inverse: construction and frozen implementation contract

Unit: rei_caloric_directional_pullback_20261028.
Workflow: user-supplied physmath-research-loop1.0.0; compatible finite-review/typed-identity rules from installed1.3.0 retained.
Repository: cosmosapjw-quantum/rei_bianchi.
Dependency: PR242 head3f299062a0d0d35c17f83a9e6081ca515e9d4c4c, research/rei_next_loop_20261028/implementation/caloric_branch.py.
Scope: a supplied finite caloric slice and its first-order variation. No astrophysical EOS, heat partition or physical temperature uncertainty is inferred.

## 1. Research choice and conventions

The preceding finite_thermal_endpoint unit and supplied-caloric-branch unit are both20/20 by inspected published evidence. Their code/input/result identities are reused. The original native audits on the same b77c7... source are separate provenance chains with different task names, hashes and targeted-check accounting; neither chain is silently renamed or double-counted.

PR242 supplies an exact rational monotone piecewise-affine inverse, enclosure and residual radius. Its frozen contract explicitly excludes derivatives/JVPs at kinks. The next construction extends that actual interface. It does not repeat generic inversion, source calibration or the already closed finite-caloric review. PR241's chemical component uses externally frozen rates and a separate REI25 binding; a physical temperature derivative of those rates is not supplied.

Candidate comparison:
1. Actual physical recipient EOS/heat certificate: useful but the current surveyed owners do not supply the required complete binding.
2. Reimplement monotone inversion/enclosure: duplicate of PR242 and rejected as next work.
3. Moving-knot inverse directional map and explicit callback composition: an unimplemented dependency with a closed algebraic construction and falsifiable small controls. Selected.

Temperature is in K. Energy knots and target are in J per the same reference volume, with the same thermal-store convention. A direction is differentiation with respect to one declared scalar parameter epsilon; temperature-knot directions are K/epsilon, energy directions J/(reference volume epsilon). Signature(-,+,+,+), c,hbar,k_B remain explicit when relevant; this scalar coordinate map introduces no metric dynamics.

Original DAG is working33/88, central last observed28/88,88 IDs/17edges,delta0. This subunit is not a new original DAG ID. Actual recipient temperature/native25/physical radii remain null; L4_ready=false/global_physical_completion=null.

## 2. Defined family and existence domain

Let n>=1 and finite rational knots
    0<T_0<...<T_n, U_0<...<U_n.
Define slopes s_i=(U_{i+1}-U_i)/(T_{i+1}-T_i)>0. The nominal branch F_0 is affine between these knots; its inverse G_0 is defined on[U_0,U_n].

Supply directions a_i=dT_i/depsilon, b_i=dU_i/depsilon and v=dE/depsilon. Consider the declared affine parameter family
    T_i(epsilon)=T_i+epsilon*a_i,
    U_i(epsilon)=U_i+epsilon*b_i,
    E(epsilon)=E+epsilon*v.
The directional result is the right derivative at epsilon=0 through this family.

Strict positive temperature and strict knot gaps persist for sufficiently small epsilon>=0. If E is strictly inside an energy segment, it stays in that segment for sufficiently small epsilon. At an interior energy knot U_j, E(epsilon)-U_j(epsilon)=epsilon*q, q=v-b_j, determines the segment side. At the lower bracket endpoint feasibility requires q>=0; at the upper endpoint it requires q<=0. For q=0 the affine family stays exactly on the moving endpoint/knot. Outward endpoint directions are outside this map's domain and return a domain refusal, not a clipped value.

For a more general differentiable feasible family with the same first derivatives, the same directional formula follows from the expansions below and local positive slope bounds. q=0 then presupposes an actually feasible family; first derivatives alone do not certify second-order endpoint feasibility. The implementation's domain claim is the explicit affine family, so it does not hide this distinction.

## 3. Interior-segment directional derivative

For U_i<E<U_{i+1}, write
    w=(E-U_i)/(U_{i+1}-U_i) in(0,1),
    T=(1-w)T_i+wT_{i+1}.
Differentiating the energy interpolation identity
    E=(1-w)U_i+wU_{i+1}
gives
    dw=[v-(1-w)b_i-w*b_{i+1}]/(U_{i+1}-U_i).
Differentiating T yields the exact first-order formula
    dT=(1-w)a_i+w*a_{i+1}
       +[v-(1-w)b_i-w*b_{i+1}]/s_i.                 (D1)
This includes temperature-knot movement and energy-ordinate movement. Differentiating only the target energy while pretending the branch is fixed omits both terms.

Equivalently, at fixed T the branch variation is
    dF|_T=(1-w)b_i+w*b_{i+1}
          -s_i[(1-w)a_i+w*a_{i+1}],
and dT=(v-dF|_T)/s_i. Thus the formula agrees with implicit caloric differentiation inside a smooth segment. No derivative of a physical EOS is manufactured by supplying numerical knot directions.

## 4. Knot directional derivative and absence of a single tangent

At E=U_j let q=v-b_j. For0<j<n,
    dT=a_j+q/s_j       if q>0,
    dT=a_j+q/s_{j-1}   if q<0,
    dT=a_j            if q=0.                       (D2)
The appropriate one-sided formula also applies at bracket endpoints when the inward feasibility sign holds.

Proof: for q>0 the perturbed target lies in the right segment for all sufficiently small epsilon>0. Its inverse is
    T_j(epsilon)+epsilon*q/s_j(epsilon).
Slopes s_j(epsilon) converge to positive s_j, giving(D2). The left-side proof is identical. For q=0, equality with the moving knot is exact for the affine family.

If s_{j-1}!=s_j, the map is generally directionally differentiable but has no single Frechet derivative at the knot. With a=b=0, the v=1 direction gives1/s_j, while v=-1 gives-1/s_{j-1}; these do not satisfy linear oddness. This is a local property of this map, not a new physical no-go theorem.

If the adjacent slopes agree, both directional formulas coincide with the linear functional a_j+(v-b_j)/s. The map has a common first differential there with respect to all knot/target coordinates: adjacent slopes vary continuously, and their first-order variation multiplies an O(epsilon) distance from the knot. A fixed-energy inverse at a bracket endpoint has only a relative/one-sided domain; the public linearization API refuses to label it an unrestricted two-sided derivative.

## 5. Explicit differential coefficients and a callback

In an open segment the derivative is linear in(v,a,b). The exact coefficient vector is:
    energy coefficient=1/s_i;
    temperature-knot coefficients=(1-w),w at i,i+1;
    energy-knot coefficients=-(1-w)/s_i,-w/s_i at i,i+1;
    all other coefficients zero.
At an interior equal-slope knot the only nonzero knot coefficients are1 for a_j and-1/s for b_j. An unequal-slope knot has no unique linearization and must report that fact. It must not silently choose a side or average slopes.

For a supplied differentiable callback f(z,T), with fixed-T Jacobian J_z and supplied column f_T, a compatible direction dz gives
    df=J_z*dz+f_T*dT.                               (D3)
D3 applies to the directional dT even at a kink, but the result is then generally a directional callback result rather than one common Jacobian matrix.

This identity requires actual derivative inputs of the declared callback. A missing physical f_T remains missing. In particular, PR241's fixed-external-rate chemical polynomial does not prove that the physical rate-dependent f_T vanishes. A caller may explicitly supply zero only for a genuinely fixed-temperature-independent model and label that model accordingly. No REI25/native30 coordinate identification is inferred here.

## 6. Common energy-coordinate covariance

For A>0 and B, transform every energy knot and target by
    U'_i=A*U_i+B, E'=A*E+B.
For a moving affine energy coordinate with derivatives A_dot,B_dot, transform
    b'_i=A*b_i+A_dot*U_i+B_dot,
    v'=A*v+A_dot*E+B_dot.
Temperature knots and their directions are unchanged. The nominal w is unchanged, s'_i=A*s_i, and
    v'-(1-w)b'_i-w*b'_{i+1}
       =A[v-(1-w)b_i-w*b_{i+1}]
because E=(1-w)U_i+wU_{i+1}. Thus D1 is unchanged. At a knot q'=A*q, so side selection and D2 are unchanged. This covers common reference-energy scaling and a consistently transformed energy origin, including their coordinate directions.

It does not permit moving an independently owned atomic binding store into thermal energy without changing both physical energy accounting and the EOS appropriately. The invariance is a statement about matched coordinates of the same declared object.

## 7. Independent exact controls, derived before code

All small controls below are dimensioned manufactured data for this scalar interface, not astrophysical EOS measurements.

A. Knots(T,U)=(1,2),(2,4),(4,10); E=7. Then T=3, s=3,w=1/2. Directions a=(1,-1,2), b=(3,-2,4), v=5 give
    dT=1/2+(5-1)/3=11/6.
The perturbed inverse can be written independently as
    T(epsilon)=(18+29epsilon+15epsilon^2)/(6+6epsilon).
Hence
    [T(h)-T(0)]/h-11/6=2h/[3(1+h)],
and, for feasible positive/negative h,
    [T(h)-T(-h)]/(2h)-11/6=-2h^2/[3(1-h^2)].
These supply exact first- and second-order finite-difference error formulas, not an implementation-to-itself roundtrip oracle.

B. At E=4 with fixed knots, v=1 gives dT=1/3 and v=-1 gives dT=-1/2. A centered difference is5/12 for every sufficiently small positive h; it equals neither right derivative1/3 nor left derivative1/2. Using5/12 as a unique Jacobian is a falsified candidate, with error1/12 against the v=1 direction.

C. At E=4, set a_1=2,b_1=3. For v=5,1,3 respectively, dT=8/3,1,2. Other finite knot directions can be zero. This distinguishes motion of the knot from energy-side selection.

D. Lower endpoint E=2,v=-1 with all knot directions zero is infeasible; upper endpoint E=10,v=1 is infeasible. Inward and tangent directions are accepted. Repeated knots, nonpositive slopes and nonpositive temperatures remain rejected by the unchanged branch constructor.

E. Equal-slope branch(T,U)=(1,2),(2,4),(3,6) has a unique interior-knot derivative1/2 for fixed knots. Nonsmooth refusal must not reject this smooth special case.

F. Apply A=3,B=-17,A_dot=2,B_dot=5 consistently to controlA. Its inverse and dT remain3 and11/6. Omitting the A_dot/B_dot terms from only one side is an intentionally inconsistent-coordinate negative control, not a physical disagreement.

G. Supplied callback J_z=((2,-1),(0,3)), dz=(1,2), f_T=(3,-2), and dT=11/6 yield df=(11/2,7/3). Both components are fixed exact expected values. A missing f_T must raise a named input dependency; supplying an empty/incorrect dimension or accidental float must reject.

H. Pinned saved C7 U,N,cv,T can define the same ideal represented branch used by PR242, with zero branch motion and v=1. Its differential is1/(cv*N), and the callback's physical fields remain null. This is one new derivative route on saved operands, not another source replay or another generic inverse-calibration stage. The old inverse results are reused. Actual run of this new derivative control remains pending authorization.

## 8. Frozen code API and allowed paths

Add code only under research/rei_caloric_directional_pullback_20261028. Reuse the exact PR242 CaloricBranch unchanged. A local source projection may carry an identical dependency file under deps for future execution; it is not called an existing Git checkout.

Required functions:
- inverse_directional(branch, energy, energy_direction, temperature_knot_directions, energy_knot_directions): validate exact data, lengths and domain; return nominal temperature, directional temperature, selected side/segment or moving-knot status, and whether an unrestricted linearization exists at the nominal point. No floats or clipping.
- inverse_linearization(branch, energy): return the above exact coefficient vectors inside an open energy segment or at an equal-slope interior knot. Raise a named NonDifferentiableKnot at unequal slopes and DomainBoundary at either endpoint.
- callback_direction(fixed_temperature_jacobian, state_direction, temperature_column, temperature_direction): exact rectangular dimensions; return D3; missing temperature_column is a named MissingDerivativeInput.
Keep argument names, dimensions and unknown-input behavior clear. No broad framework, automatic physical source import, inferred composition, replacement tolerance, source calls, IVPs or whole old-suite replay.

The implementation may reuse the exact decoder exposed by the pinned dependency. Dependency file identity must be recorded. The current host has no Git checkout; remote connector-backed branch publication and a clearly named local source projection are the available paths. No new clone/worktree is required.

## 9. Verification, figures and execution authority

One future bounded test invocation is sufficient for changed behavior: exact controlsA-G, targeted boundary/type errors, exact h-dependent checks fromA/B, and optional saved-source derivativeH in the same invocation. No unchanged PR242 test suite is to be rerun. A figure script should consume saved new results after that invocation, drawing(a) knot directional map and the false centered slope, and(b) the analytic first/central difference errors fromA. It must label manufactured inputs and inspect the rendered figure before C8 admission.

All newly authored tests, plotting and saved-source derivative evaluation are NOT_RUN at preparation. Historical numerical reservations are closed. Latest inspected PR242 budgets restore original planning10/presentation30 after charged16.586967885/50.928518494, with unknown overhead retained. Current-task budget authority must be resolved before local scientific/figure execution; do not move work to a foreign ledger or relabel a new allowance as unused old balance. Native reasoning, source reads, code authoring, independent static review and explicitly requested text publication/backups proceed within their existing authority.

The explicit next execution proposal will name absolute cumulative ceilings, one command, worker/wall/memory cap, measured child accounting and a finite repair scope. Whole-session/remote/model overhead remains UNKNOWN_NOT_ZERO. Main595.225063/600 NO_MORE_IVPs and owner reservations remain unchanged.

## 10. Claim and completion boundaries

The mathematical result is a constructive derivative of a supplied finite monotone interpolation inverse; it makes no literature novelty claim. It is useful to a caloric consumer and a supplied callback, but physical composition/heat/rate derivatives remain owner inputs.

R1-R5 may be completed from the actual survey, definitions, candidate discrimination and proof. R6 requires the actual independent review. R7 can distinguish the candidate interpretations using the exact analytic controlsB/C without a new physical source run; the additional numerical checks must retain their separate NOT_RUN state. Theory completion and authored implementation are distinct from C6-C8 executed acceptance. C9 static review alone does not admit unexecuted code. C10's resumable checkpoint does not create a successful runtime result.

