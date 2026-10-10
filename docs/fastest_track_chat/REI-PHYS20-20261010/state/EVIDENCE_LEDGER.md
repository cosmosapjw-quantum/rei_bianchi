# Evidence ledger

| ID | Claim | Evidence status and support | Source |
|---|---|---|---|
| E01 | Exact Bianchi-I E and direction | literature-supported / derived; supports | Fleury–Pitrou–Uzan arXiv1410.8473v3 Eqs4.1–4.5; report§3 |
| E02 | Birth Jacobian vs current solid angle | derived; source inspected, no Rust execution | report§3; pinned paired_runtime.rs56–61,118–131,224–225; bianchi_i.rs185–208 |
| E03 | First variation of absorption and heat with survival memory | derived / numerically checked | report§4; evidence/directional_kernel_v2.json,81 checks |
| E04 | Smooth isotropic coupled scalar first derivative=0 | derived / conditional; literature contextual | report§5; MGE astro-ph9808163v2 Eqs70–72 |
| E05 | Exact midpoint Q and selected/generic STF difference | derived / exact-arithmetic checked | independent/angular_moments_results.json |
| E06 | Free-energy quadratic coefficient and finite-grid bias | derived / numerically checked | report§6; independent Fraction/Decimal80 evidence |
| E07 | Fixed-q birth artifact and normalized-J residual | derived / numerically checked | report§6.2; independent report |
| E08 | Threshold cusp | derived / numerically checked | report§8; evidence/threshold_cusp.json |
| E09 | Actual scalar gas second-order coefficient | unresolved / missing | target PHYS21; not replaced by frozen gas probe |
| E10 | Physical/production admission | HOLD / not supplied | inherited scope; no new gas IVP |

Git/blob/SHA values establish input byte identity; they do not establish physical validity. Numerical differences are measured comparisons, not rigorous global remainder intervals. Independent decision-review identifies its own evidence and limitations.
