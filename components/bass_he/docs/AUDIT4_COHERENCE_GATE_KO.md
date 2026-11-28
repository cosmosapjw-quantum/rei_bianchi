# AUDIT4 — DR10 coherent-vs-stochastic transport gate

## 1. Isolated double passage

For a single two-state crossing with one-pass probability p, two incoherent population updates give P_M = 2 p (1-p).

A coherent two-path treatment can be written, after absorbing dynamical and Stokes contributions into a total phase Phi, as P_coh(Phi) = 4 p (1-p) sin^2(Phi).

Uniform phase averaging gives exactly 2 p (1-p), so the Markov result is the phase average for this isolated symmetric double-passage problem. The coherent envelope is [0, 4 p(1-p)], twice the Markov mean at its maximum. For any nontrivial p, the phase-ignorance half-width about the Markov mean is therefore 100% of that mean.

Wolfram checks the phase average and the two-pass stochastic matrix identity. Unit tests independently lock both formulas.

## 2. Why this does not close the full Eq. (50) network

The CPC 2023 Eq. (50)-(52) assembly multiplies probability matrices and therefore carries no complex phase. Stolterfoht et al. 2010 explicitly describe the impact-parameter oscillations in He2+ + H as Stückelberg interference produced by coherent contributions from two localized transition regions. Thus the current probability transport is a phase-erased model, not a coherent prediction.

The isolated two-pass phase-average equivalence cannot simply be promoted to the five-branch network with P_rot: multiple paths can recombine, branch phases are correlated, and the rotational block mixes channels. A coherent extension would need amplitude-level crossing matrices with Stokes phases, dynamical phase integrals between events, a phase convention through the rotational block, and a physical treatment of the upper-shell absorbing sink. Alternatively, retaining the Markov model as physics requires an explicit random-phase/decoherence authority.

## 3. Numerical stress at Appendix-A B=0

Using the factor-2 single-pass lane favored by DR9B: at 5 keV/u the Q23 branch has p≈0.2400, so the isolated double-pass Markov value is 0.3648 while the coherent envelope is 0–0.7297. At 0.5 keV/u Q23 has p≈0.01097, giving Markov 0.02170 and coherent envelope 0–0.04341. These are branch-level stress values only; they are not full cross-section error bars.

## 4. Gate

- isolated double-pass Markov = uniform phase average: CLOSED;
- full Eq. (50) coherence equivalence: OPEN;
- random-phase/decoherence authority: OPEN;
- coherent multi-branch transport: NOT IMPLEMENTED;
- physical production cross section / production CT2: CLOSED.


## 5. Same-system hidden-crossing phase authority

Janev, Pop-Jordanov & Solov'ev (J. Phys. B 30, L353, 1997) provide the missing same-system phase structure explicitly. They write q=exp(-xi), so the one-pass transition probability is p=q^2=exp(-2 xi). For a square-root branch point the topological phase is gamma=pi/2 in the adiabatic v->0 limit, and the two-pass probability is P=4 p(1-p) cos^2[chi(b)+gamma]. This is algebraically equivalent to the generic sin^2 form after the pi/2 phase shift.

The same paper states that chi(b) varies inversely with v and oscillates rapidly with impact parameter at sufficiently small v. Under the impact-parameter integral for the total cross section, cos^2 can then be replaced by its mean 1/2, so the phase does not affect the total cross section in the adiabatic region. It also reports a modified ARSENY evolution matrix that included dynamical and topological phases.

This materially refines the gate: phase averaging has direct hidden-crossing authority for adiabatic total cross sections, but not automatically for differential probabilities, state-resolved outputs, finite-v multibranch interference, or the present absorbing-sink semantics.
