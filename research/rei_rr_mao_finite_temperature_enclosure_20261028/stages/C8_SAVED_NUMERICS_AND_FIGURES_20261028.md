# C8: source-bound numerical and saved-data figure readback

**PASS_SCOPED_SELECTED_NUMERICS_AND_SAVED_PLOTS**, not a whole-solver convergence certificate.

Pinned actual GitHub Actions run [40708427630](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/40708427630) returned 60 Taylor records. For all 48 nonzero log-temperature steps, `abs(residual)/radius` ≤ **0.9182188000110807073** (worst ion 3:3, RR rate, h=-1/128); 12 zero-step records are separate. Four unequal tiny-log-step cases successfully returned with recorded high-precision h inside the outward h interval. Ten refusal controls were present and successful; 50-digit and 70-digit boxes for two selected quantities were nested.

Three saved-output figures (RR rate, selected Mao conditional kinetic loss, and residual/bound ratio) were generated **without re-executing the scientific solver**, opened and inspected. One bounded display-only correction removed false continuous line connections between unrelated discrete ion categories; initial plots are retained for comparison. The original PR250 plotting script was **not** executed in this runtime. Nothing here certifies floating callback roundoff, broad physical temperatures, or observational completeness.

Numerical summary and raw CI zip are preserved in the 27-entry scientific packet: SHA256 `afb46eb70d53d64c3ee1847d9774676fa8754155f6b9e975a1b70ce9b73cc354`, 617002 bytes, Drive `1DHjNv7ySUsS7QAsmcM6IEjszhw__WkTp`, Dropbox `id:BSpOijBcT10AAAAAAEGpOQ`. Both actual completed/upload and separate metadata size 617002 ACK confirmed.

RR unit **18/20** (theory10 + coding8), C9 `PENDING_FRESH_NATIVE_POST_EVIDENCE_REVIEW`, C10 `PENDING_C9`. Existing static reviewer `/root/rr_mao_native_reviewer` is not silently promoted. Original DAG working33/88, central last28/88, delta0; real recipient temperature/native25/physical radii null.
