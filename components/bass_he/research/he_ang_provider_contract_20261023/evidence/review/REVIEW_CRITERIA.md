# HE-ANG independent review criteria

Reviewer: `/root/heang_independent_review`. Workflow 1.0.0 / approval 0.2.
Role: independent review of the source/frame/event provider contract and its changed implementation. No authoring of the implementation, no HE-X1/HE38 scientific execution, and no remote mutation.

## Fixed authority and reused evidence

- Central handoff and HE-ANG contract: `rei_bianchi@0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`, `research/orchestration_longterm_20261023/assembly/HANDOFF_BASS_HE_KO.md` and `thermal/BASS_HE_LONGTERM_CONTRACTS.json`.
- HE-X1 science: `eb03981d15ad291375dd6d574a9c28809f85fc02`; final frozen API, independent review and `raw_outcomes.json` are reused. Their 32 fixture decisions / 181 assertion predicates are historical evidence, not executions of this reviewer.
- BASS_HE baseline: `10e24aeaae21cf8e1427fba64233631d15444e67`; AGENTS and HE38 finite-mass derivation read from verified recovery output.
- Existing completed budgets remain separate and nontransferable. HE-X1's pre-Python launch has CPU `UNKNOWN_NOT_ZERO`; its exact residual cumulative allowance is not established. A fresh contract budget cannot silently repair or replenish it.

## Admission questions

1. Does every cross-section, partition, inclusive electron moment and ion recoil moment bind to the same immutable differential source, incident-energy convention, integration domain and normalization?
2. Is the event measure count one, the inclusive electron measure count two, and the proton measure count one? If roles are labelled, is exchange symmetrization described without multiplying the event rate?
3. Are the full outgoing momenta supported on the stated nonrelativistic additive-mass energy and momentum shell? Does a marginal-only provider expose its missing event-correlation obligation instead of fabricating ion moments?
4. Are common-frame, incident-axis, primary-energy and relative-flux mappings explicit? Are raw number/first/second moments retained for a Galilean boost, including the reactive number term?
5. Does partial angular/slow-electron/incident-energy coverage remain partial? Does the implementation refuse an unrecorded renormalization or extrapolation?
6. Are source/model uncertainty, quadrature error and represented-input arithmetic evidence separate? A numerical model check at `1e-8` does not become physical calibration.
7. Does any PASS have a precisely limited action? A structural event packet or a manufactured fixture must not activate a calibrated physical provider or replace the HE38 angular law.
8. Do data, receipts, cumulative budgets and failures persist through review and corrections? Are actual execution predicates distinct from independent physical cases?

## Independent two-cone calculation

At fixed incident COM energy choose `a·b=0`, `|a|=|b|=1`, `s=±1` uniformly, with `b` uniform in the transverse circle and masses `m,M>0`. Both constructions have electron momenta of magnitude `p`:

\[
A:\quad q_1={sp\over\sqrt2}(a+b),\quad q_2={sp\over\sqrt2}(a-b),\quad q_p=-s\sqrt2p\,a,
\]
\[
B:\quad q_1={p\over\sqrt2}(sa+b),\quad q_2={p\over\sqrt2}(-sa+b),\quad q_p=-\sqrt2p\,b.
\]

In both cases `q1+q2+qp=0`, electron kinetic energy is `p²/m`, ion kinetic energy is `p²/M`, and the same incident excess energy is `E−I=p²/m+p²/M`. Direct outer-product expansion gives

\[
R_e=p^2\langle aa^T+bb^T\rangle=p^2\bigl[aa^T+(I-aa^T)/2\bigr],
\]
\[
R_{p,A}=2p^2aa^T,\qquad R_{p,B}=p^2(I-aa^T).
\]

The full electron inclusive measure agrees, since each outgoing electron has the same two cones at cosine `±1/√2`, the same momentum magnitude, equal signs, and uniform azimuth. Exchange symmetry follows by `b→−b` in A and by `s→−s` in B. Both laws are axially symmetric about `a`. With `S_s=R_s/(2m_s)` and `D_s=(3aᵀS_sa−tr S_s)/2`,

\[
D_e={p^2\over4m},\quad D_{p,A}={p^2\over M},\quad D_{p,B}=-{p^2\over2M}.
\]

Thus this explicit kinematic pair has the same electron marginal and scalar energy ledger but different ion second moments. It is a contract stress test within the stated measure class; it is neither a claim about two realized hydrogen amplitudes nor a novelty/global impossibility theorem. The relevant mechanism is the missing cross tensor `C=∫(q1q2ᵀ+q2q1ᵀ)dΣ`, because `Rp=Re+C` in the COM frame.

## Independent frame calculation

For a species of mass `m_s`, a common Galilean shift `p'=p−m_s U` transforms count-weighted moments as

\[
N'_s=N_s,\quad P'_s=P_s-m_sN_sU,
\]
\[
R'_s=R_s-m_s(UP_s^T+P_sU^T)+m_s^2N_sUU^T.
\]

A subsequent orthogonal rotation acts by `P''=OP'`, `R''=OR'Oᵀ`. These formulas also apply to signed net reaction measures. Their number terms must therefore be retained even when total translational mass and net total momentum are conserved. Passing `S` alone does not generally determine a boost of a marginal distribution.

The provider contract should identify the stationary-target map `E_COM=ζ E_lab`, `ζ=(M+m)/(M+2m)`, when it uses the inherited additive-mass convention. A moving target requires the relative-velocity/flux and incoming distribution contract. A differential density must account for its actual coordinate Jacobian or be transferred as a measure pushforward with complete branches.

## Current review status

Independent algebra and acceptance criteria prepared; new unit's actual documents and implementation await review. Scientific executions by this reviewer: 0. No final PASS is issued by this preparation document.
