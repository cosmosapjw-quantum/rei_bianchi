# R5: PR166 source-age boundary-layer audit (2026-10-16)

Additive scientific note. Source: Draft PR166 frozen HEAD \`553ce556d9f8662290c000ec675c7e6007c9d895\`; actual native source \`35d9747a0bbedcafdb568467ce7c1e7a25f965b6\`. The original NCP output is read-only; no production code/checkpoint was modified or rerun.

**Provenance:** Original Dropbox/Drive-restored ZIP \`REI_SOURCE_AGE_NATIVE_OWNER_BIND_20261016_v1.zip\`, size 6,380,408 bytes, SHA-256 \`2ebab11829b793eb19a0b91e5d04a3a8637e346e456ac0931c372585ef7e21de\`, local ZIP CRC PASS. Read the actual stored \`evidence/repaired_local/snapshot_q{q}_axis1_level{1,2,4}.txt\` arrays by summing \`Cohort.birth.original.number\` and \`Cohort.surviving.number\`.

At PR166 driver q_ref=0, birth ages n=8/16/32:
- Total births/H: 7.295271534018042e-05 / 7.295271810132430e-05 / 7.295271879161027e-05, relative span 4.73105e-08.
- Surviving photons/H: 1.334404090241785e-10 / 7.267135767582913e-09 / 7.507668554379102e-08.
- Last cohort / all surviving photons: 0.9998839175104116 / 0.9996326898023306 / 0.9962224697350944.
- Last cohort -ln(Nsurv/Nborn), rescaled to whole x interval: effective 178.18 / 206.28 / 218.97. **These are spectral/cohort-averaged effective exposure diagnostics, NOT microscopic Verner opacities.**

Same late-birth dominance was observed in both signed driver q_ref=±0.1. The nearly unchanged total birth and growing survivor strongly support **under-resolved source-age survival boundary layers** as a candidate mechanism. Not proof of the unique origin of nonlinear Grackle age-trend anomalies.

For constant nonnegative source j, frozen opacity κ, L=Δln a, τ=κL, S=jL:
\`\`\`
N_cont = S (1-e^-τ)/τ = S φ1(-τ)
N_mid(n) = S (1-e^-τ) / [2n sinh(τ/(2n))]
N_mid/N_cont = z/[2sinh(z/2)], z=τ/n
N_mid(2n)/N_mid(n) = cosh(τ/(4n))
N_mid/N_cont = 1-z²/24+O(z⁴)
\`\`\`
Wolfram Language actual result for ratio/doubling/continuum limit/old-stock derivative is \`{0,0,1,0}\`. For n8→16 and n16→32 observed ratios at q_ref=0, a **single** frozen-opacity inverse fit would yield τ≈150.10 and τ≈193.66, inconsistent. Thus the actual native result cannot be certified by one constant-κ toy.

Positive source-exposure update: \`Nnew=Nold exp(-τ)+S φ1(-τ)\`. Photon absorption (frozen κ_i competing risks) is \`A=Nold(1-exp(-τ))+S(1-φ1(-τ))\`, \`A_i=A κ_i/Σκ_i\`; it is nonnegative with \`Nnew+ΣA_i=Nold+S\`. This is a conditional frozen gas/energy result, not nonlinear native solver parity.

**Separate DOP853 issue:** The original PR166 independent SciPy RHS failed on an internal negative photon moment at call 291 (N=-1.0561176359772685e-20/H). A new manufactured scalar IVP \`dN/dx=-30000 N,N0=9e-6\`, \`DOP853 rtol=2e-9,atol=1e-15\` also fails the strict internal-stage positivity guard at N=-3.7439977e-17. This demonstrates a viable stage-overshoot mechanism, NOT proof of the original failure's unique cause. Use a positive mild/integrating-factor reference as an independent route without clipping.

**DAG:** \`R5_NATIVE_READBACK_EXACT_BOUNDARY_LAYER=COMPLETE\`; \`C5_POSITIVE_AGE_REFERENCE=IN_PROGRESS\`; \`C7_C8_INDEPENDENT_TESTS=PENDING\`; \`C10_BACKUP_PUBLICATION=PENDING\`; \`NATIVE_POSITIVE_REFERENCE_INTAKE=READY_AFTER_ORACLE\`; full EoR scientific admission \`NOT_ISSUED\`.

Original archival ZIP already double-cloud restored under PR166. This stage's new frozen-theory/diagnostic source + cohortwise JSON are preserved separately in the sandbox R5 capsule (24,627 bytes, SHA256 \`60a9be256ae889f018976d400435fcc388061edfedbb35dbe3ec23f5136bee23\`). Dropbox/Drive new-stage upload is **NOT_VERIFIED**: the Library container bridge returned \`container_session_expired\`. Do not claim a new dual-cloud backup from the prior PR166 archive. Native subagent NOT_RUN (no host dispatch tool).