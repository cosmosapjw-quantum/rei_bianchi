# Negative results and correction record

1. REJECTED_GENERALIZATION: tr(shear)=0 alone does not establish zero scalar response for every finite angular grid. Exact midpoint Q differs from I/3; same-eigenvalue rotated shear creates a linear angular artifact. Physical source/default unchanged.
2. REJECTED_GENERALIZATION: selected epsilon-sign symmetry alone does not establish quadratic onset. A monochromatic threshold positive-part response gives |epsilon| cusp.
3. REJECTED_GENERALIZATION: source J normalization alone does not establish exact birth-time independence on finite grids. The remaining sigma^2*b*Delta coefficient is 2/(3*N^2)-7/(6*N^4).
4. REJECTED_INTERPRETATION: absorption rate per emitted photon and absorption rate per current physical solid angle are different; present-angle conversion adds -3*DeltaBeta.
5. NUMERICAL_IMPLEMENTATION_CORRECTION: directional_kernel v1 initialized xHI via Decimal's default28-digit subtraction. Version2 sets context60 before constants. Original evidence retained; successful derivative comparisons in v1 did not establish the stronger exact-input wording. The reported rounded results are unchanged.
6. RUNTIME_ENVIRONMENT: independent reviewer attempted mpmath, unavailable; import-stage failure preserved in its own evidence. Reviewer switched to standalone Decimal70/Simpson without package installation. This is not a failed physics claim or solver run.
7. HISTORICAL_FAILURES_PRESERVED: [160,161] FAIL; tick160; auxiliary escape FAIL. No causal attribution from current angular findings.

No native runs, gas IVPs, old PHYS19/BRIDGE13/14 proof reruns, or full raw campaigns were invoked. No repeated full review was requested.
