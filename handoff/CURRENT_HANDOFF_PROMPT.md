# CURRENT HANDOFF PROMPT — rei_bianchi

Use this prompt at the beginning of a new work thread. The repository is the
sole durable source; do not inherit transcript-only numerical claims.

---

@Web+Wolfram Treat this as a durable continuation of the private `rei_bianchi`
project.

Canonical repository:

```text
https://github.com/cosmosapjw-quantum/rei_bianchi
```

External primordial-recombination repository:

```text
https://github.com/cosmosapjw-quantum/rec_bianchi
```

Before science work:

1. Read `PROJECT_STATE.json`, `docs/science/current_00_READ_FIRST.md`,
   `docs/provenance/DURABLE_STAGE_LEDGER.csv`, `external/rec_bianchi.lock.json`,
   this file, and the latest stage `00_READ_FIRST.md`.
2. Run `python scripts/verify_repo.py` and verify the latest stage
   `SHA256SUMS`.
3. Run `scripts/update_rec_bianchi_lock.sh`; record an exact remote SHA or
   explicit unavailable status. Query the authenticated GitHub connector when
   exposed. Read `external/REC_BIANCHI_MONITORING_POLICY.md`. A changed SHA
   requires deliberate adapter/input-lock review; never implement a
   recombination surrogate.
4. Verify every canonical artifact and logical-output hash used by the next
   stage.
5. Create the next durable stage directory, input lock, stage state, receipts,
   manifest, and `SHA256SUMS` before calculation.

Project objective:

Derive and implement the equations needed to extend homogeneous reionization
and CAMB-level CMB transfer to all 11 Bianchi types with nonlinear large shear
and finite tilt, using tetrad and 1+3 formalisms. Metric signature is
`(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, `k_B` remain explicit unless a
stage declares otherwise.

Current durable verdict:

```text
P0.5-B2C2B0C-R2C-R1-RATE-DERIVED-POSITIVE-MULTIRATE-RELAXATION-CONE-LOCK
DURABLE_FAIL_CLOSED_R2C_R1_MACRO_SHARED_COMMON_EQUILIBRIUM_MULTIRATE_CONE_NOT_ALL_LANES_REACHABLE
Production node chemistry authorization: false
R2C-R2 authorization: false
B2C2B authorization: false
R2C-R1A preflight authorization: true
```

R2C-R1 froze 3,240 rate-interval rows before feasibility. It tested 540 macro
cases. Forty-three equilibrium boxes were feasible, all 43 had certified
analytic paths, and 27 passed the complete refinement gate; no shape lane
passed all 180 cases. The 497 equilibrium no-go cases have self-contained and
independently replayed Farkas certificates: 209 cycling-capacity, 125 G1,
157 G2a, and six macro-mass-cap rows. Maximum replayed KKT relative
stationarity was `2.03e-16`; endpoint and current-Gamma residuals were
`5.71e-17` and `9.14e-16`; 540 structural-zero rows remained exact. No node
rate fitting, clipping, dynamic KL repair, or inter-macro moment transport was
used.

The mode-count theorem in the stage proves that adding more positive
exponential modes cannot enlarge the endpoint equilibrium box while the same
common equilibrium and locked rate interval are retained. The result is
conditional on macro-shared rates. Deterministic node-local rates derived from
local density, temperature, opacity, current, and transfer fields remain an
open, simpler alternative and must be tested before a coupled generator is
introduced.

Native Wolfram and the requested special-function plugin were not exposed in
the R2C-R1 runtime. The executable `.wl` script and independent SymPy,
90-digit Decimal, and 100-digit mpmath fallback passed; no plugin execution is
claimed. The final native Git read probes for both private repositories failed
because `github.com` DNS resolution was unavailable. The last connector-known
`rec_bianchi/main` SHA is `0d24bf7fc6b2643f0bf5fd7f693a6ebc3889958d`, not a
fresh R2C-R1 verification. No push was attempted; the owner performs the local
push.

Next exact execution instruction:

# R2C-R1A node-local physics-derived rate-field cone preflight

Execute
`P0.5-B2C2B0C-R2C-R1A-NODE-LOCAL-PHYSICS-DERIVED-RATE-FIELD-CONE-PREFLIGHT`.

1. Create the durable R2C-R1A directory, input lock, stage state, receipts,
   manifest, and `SHA256SUMS` before calculation.
2. Keep every R2A/R2B/R2C endpoint, projection, photon/H/He ledger, and every
   R2C-R1 rate/Farkas/KKT/trajectory certificate canonical. Do not widen a rate
   bound from `dual_single_bound_extension_diagnostic.csv`; it is
   non-authorizing.
3. Derive node-local positive rate evidence from explicit local physical
   fields at both inherited endpoints: gross mass transfer for `M`; local
   photoionization/recombination/collisional/transfer activity for `I`; local
   heating/cooling/expansion/thermal transfer for `U`; and
   `c(1+z) kappa_ig/Mpc` plus explicit group-boundary/source terms for `J_g`.
   Derive `C` only from an independent local cycling/recombination law. If no
   such law exists, mark `UNIDENTIFIABLE_REQUIRED_RATE` rather than insert a
   nuisance value.
4. Node dependence must be deterministic from physical inputs. Do not optimize
   an unconstrained independent rate per node. Any uncertainty scaling must use
   a small predeclared macro-shared hyperparameter vector whose bounds are
   locked before cone feasibility.
5. Audit tiny-support tails without discarding them. Record zero-support,
   floor-sensitive, finite, and unidentifiable rows separately. Keep all units
   explicit until the final `Myr^-1` conversion.
6. Commit the node-local rate-field lock before examining feasibility. Its
   weighted macro reduction must reproduce inherited macro process evidence
   within a prelocked tolerance or fail closed.
7. Test one-mode endpoint/equilibrium and analytic cone feasibility with the
   fixed local field or macro-shared hyperparameters. Do not add another mode;
   R2C-R1 showed that mode count is not the first missing freedom.
8. Preserve macro/group/global endpoint moments, current-Gamma, H/He nuclei,
   mass/volume caps, and `J_G1+J_G2a<=C`. No clipping, cloud-mass inversion,
   dynamic KL repair, or inter-macro transport.
9. Emit self-contained KKT/Farkas certificates and Wolfram checks of local-rate
   formulas, dimensions, endpoint identities, and exact zeros. If Wolfram is
   unavailable, retain the `.wl` script and independent high-precision
   fallback.
10. Do not start production node chemistry, unresolved subtraction, front/Q_M,
    source/fesc calibration, primordial recombination adapter/surrogate, CAMB
    transfer, or Bianchi feedback.

Decision rule:

- all-lane deterministic local-rate pass: authorize a bounded finite-history
  audit;
- identifiable local-rate failure in coupled current/capacity or mass cones:
  authorize a separately prelocked Metzler-generator stage in
  `q_gamma=(C-J_G1-J_G2a,J_G1,J_G2a)` and `q_M=(M,M_cap-M)`;
- unidentifiable required local rate: fail closed and report the missing
  physical source/operator term, without fitting a surrogate.

Repository/update policy:

- Save every accepted or fail-closed stage under `stages/` and/or
  `artifacts/compact/`.
- Update `PROJECT_STATE.json`, this handoff, the artifact registry, and durable
  ledger in the same durable-stage commit.
- Commit each durable stage and tag major locks.
- Never claim a push unless `git push` and subsequent `git ls-remote` both
  succeed and the remote SHA is recorded.
- Preserve failed attempts separately; never overwrite them with later
  success.

---
