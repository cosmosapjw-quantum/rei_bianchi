# Independent analytic review: bounded isotropic kinetic pressure

Date: 2026-10-24. Reviewer: **/root/source_review**, a native separately invoked reviewer with the same inherited model family. No cross-family model identity is asserted. Reviewed item: next_pressure/THEORY_KO.md, previously read in full. This is a finite analytic review of its stated measure problem; source code review belongs to the separately assigned evidence reviewer.

## Verdict and scope

**PASS_SCOPED — theory only.** The displayed derivatives, chord and Jensen bounds, exact gap, attaining measures, zero cases, nonrelativistic error bound and stock/rate units are correct under the stated assumptions. No actual analytic finding was identified. No numerical calculation, scientific child, CAS, import, compile or render was performed. Pressure numerical validation and physical pressure/stock closure remain **NOT_ADMITTED**.

This result is independent of the completed L1 selected-summary consumer admission. It does not consume or inherit that child's allowance and introduces no additional L1 gate.

## Assumptions and relativistic kernel

The theory fixes M=m_e c^2>0 and a finite nonnegative measure nu supported on [0,L], with N=integral dnu and U=integral k dnu (THEORY_KO.md:11). All energies k,L,M use the same unit. Its kinematic identities give

\[
g(k)=p_{\rm phys}v
=\frac{k(k+2M)}{k+M}
=k+M-\frac{M^2}{k+M},\qquad
\Pi=\frac13\int g(k)\,d\nu(k).
\]

This follows directly by substituting p_phys^2 c^2=k(k+2M) into v=p_phys c^2/(k+M); no unrecorded numerical or empirical premise is needed (THEORY_KO.md:15, :20). Pi is the isotropic scalar pressure moment; the trace of the associated isotropic stress is 3 Pi.

Differentiation gives

\[
g'(k)=1+\frac{M^2}{(k+M)^2}>0,\qquad
g''(k)=-\frac{2M^2}{(k+M)^3}<0.
\]

These match THEORY_KO.md:30 and :31. Thus g is increasing and strictly concave on the stated nonnegative-energy domain, with g(0)=0.

## Sharp interval and endpoint witnesses

For L>0 and N>0 with 0<=U<=NL, concavity puts g above the chord from 0 to L:

\[
g(k)\ge \frac{k}{L}g(L).
\]

Integrating gives the lower endpoint in THEORY_KO.md:35. Applying Jensen's inequality to the probability measure nu/N gives the upper endpoint in THEORY_KO.md:37:

\[
\boxed{\frac{U(L+2M)}{3(L+M)}
\ \le\ \Pi\ \le\
\frac{U(U+2MN)}{3(U+MN)}}.
\]

The measures written at THEORY_KO.md:39 and :42 are admissible and attain these endpoints:

\[
\nu_{\min}=(N-U/L)\delta_0+(U/L)\delta_L,\qquad
\nu_{\max}=N\delta_{U/N}.
\]

Their masses are N, first moments are U, weights are nonnegative, and support lies in [0,L]. Consequently the bounds are sharp for the stated class of finite nonnegative measures, which includes atoms. Strict concavity explains the endpoint/monoenergetic equality conditions. This does not assert that an arbitrary fixed physical source attains an endpoint.

Subtracting the two formulas yields exactly the displayed width (THEORY_KO.md:44):

\[
\Pi_{\max}-\Pi_{\min}
=\frac{UM(NL-U)}{3(U+MN)(L+M)}.
\]

The denominator is positive for the main case. The width is positive for 0<U<NL and vanishes at U=0 or U=NL. The illustrative N=U=L=2, M=1 witness at THEORY_KO.md:57 agrees with direct symbolic substitution: the endpoint values are 8/9 and 1, attained by delta_0+delta_2 and 2 delta_1. This is inspection of the displayed exact example, not an executed numerical fixture or a CAS result.

The constructive difference between these admissible measures shows the finite insufficiency of N and U to specify Pi uniquely in the interior. It supports the stated interval, without claiming novelty, an empirical error bar, or a broad no-go theorem.

## Zero cases and nonrelativistic comparison

The separately stated zero branches (THEORY_KO.md:47) avoid undefined divisions. N=0 implies the zero measure and U=Pi=0. L=0 implies support only at k=0 and likewise U=Pi=0. For a nonnegative measure on nonnegative k, U=0 concentrates the measure at k=0 up to measure-zero sets, again giving Pi=0. The endpoint U=NL with L,N>0 concentrates the measure at L and collapses the interval.

The nonrelativistic comparison at THEORY_KO.md:49 follows from the exact identity

\[
2k-g(k)=\frac{k^2}{k+M}.
\]

Since k/(k+M)<=L/(L+M) on [0,L],

\[
0\le \frac{2U}{3}-\Pi
=\frac13\int\frac{k^2}{k+M}\,d\nu
\le\frac{UL}{3(L+M)}.
\]

The derivation and sign are correct. The document does not misidentify 2U/3 as the exact relativistic pressure.

## Normalization, rate versus stock, and limits of use

THEORY_KO.md:20 explicitly distinguishes a population measure from an injection-rate measure. With N a stock count per Href and U an energy stock per Href, Pi has energy per Href; multiplication by n_Href and the eV-to-J conversion produces physical pressure. With N a count injection rate and U an energy injection rate, Pi is an injected pressure moment per proper second. It is not the current accumulated pressure stock.

The formulas are homogeneous in the measure: scaling N and U by the same nonnegative factor scales the interval by that factor, with M and L unchanged. The proposed substitution N=A, U=K, L=E_max-chi and once-only target multiplier m=a X_HI at THEORY_KO.md:63 is therefore dimensionally appropriate for the selected rate measure, subject to exact represented feasibility 0<=U<=NL. Independently rounded summary feasibility is an input condition, not a new donor uncertainty certificate. B, P and their residuals remain outside this pressure reconstruction and must stay unchanged.

Isotropic STF zero alone does not determine this scalar pressure; pressure-injection information alone does not close the later stock evolution. The theory expressly retains the need for initial-distribution, transport/redshift/stopping or a separately declared approximation before such a stock/Einstein use (THEORY_KO.md:69). A future raw-atom route requires its actual payload and support/schema binding; it was not evaluated here.

## Review boundary

The root-supplied bibliographic context was not independently re-queried for this review; the mathematical result was checked from the displayed assumptions and formulas. No new source code was read or changed in this analytic review, no pressure runner was invoked, and no scientific resource allowance was spent or transferred. Findings: none. Theory preparedness is PASS_SCOPED; numerical pressure evidence is NOT_RUN and physical pressure closure is NOT_ADMITTED.

