**MAJOR — premature coefficient rounding changes the certified map.** At [checker.py:140](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/.cuh/fastest-track/REI-F04-CERT/checker.py:140), `float(1.923)*float(.470)` rounds before entering MPFI. The frozen [Rust expression](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/ft03_interval.rs:107) multiplies the individually pinned parameters outward.

The exact coefficient difference is approximately `−3.3475444638497721e−17`. My single finite Sage probe found, at **all three frozen centers**:

- Intended thermal RHS minus checker RHS: approximately `+1.749e−33`.
- Checker interval diameters: `8.49e−72` to `1.09e−71`; the intended values lie outside them.
- Four gradient and sixteen Hessian entries likewise have disjoint intervals.

Thus the current proof does not establish the declared real-valued map. This finding **does not demonstrate failure of the local-error or public-width thresholds**.

Minimal repair: promote both operands before multiplication, using `R(float(1.923))*R(float(.470))`, then perform the parent-owned validation closeout. No other inexact premature float product was found on this arithmetic surface; line 139 multiplies by exactly 1 or 2.

Evidence: [probe source](/tmp/REI-F04-CERT-REVIEW-01a1081a/coefficient_probe.py), [exact argv](/tmp/REI-F04-CERT-REVIEW-01a1081a/argv.json), [results and identities](/tmp/REI-F04-CERT-REVIEW-01a1081a/stdout.json). Telemetry task `REI-F04`; exit `0`.

Otherwise, inspection found no additional defect in the scaled RHS, Krawczyk inclusion, Neumann inverse bound, central-error propagation, implicit Hessians, observable Taylor bounds, or shared-parent half composition. All eleven frozen scope hashes matched before/after; source-manifest and interval-dependency hashes also matched at HEAD `890439782b940af8e9017f65de06f70150669a83`.

I executed only the discriminating probe; the stored 3,591-witness certificate was inspected, not regenerated. Repository files were unchanged. Final validation remains with the parent; physical and historical admission remain `HOLD`.

<oai-mem-citation>
<citation_entries>
MEMORY.md:3358-3359|note=[kept review focused on scientific correctness and reproducibility]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>
