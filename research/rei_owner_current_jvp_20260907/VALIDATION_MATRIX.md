# Sequential local review

One same-assistant review round, PHYS-MATH first and PHYS-MATH-CODE second.
Contract: PROOF_AND_SCOPE.md, WORK_UNIT.json and LOCAL_CODEX_HANDOFF_KO.md, with
the owner's local execution instruction. No independent reviewer was used or
certified. The validation skill's scientific rows are recorded here. No
production promotion or proof-completion approval follows.

## 1. PHYS-MATH

| Item | Status | Evidence / limit |
|---|---|---|
| Exact-real source reduction | PASS within stated domain | `_global_raw_values`, `_condition`, `_allocate` give `j_si=J*c_s*N_si/R`. Fixed positive species sigma cancels within each active marginal; global R remains. |
| Coefficient convention | PASS | Actual NH0/YHE/MPC/sigma construction and owner masks are bound in INPUT_INSPECTION. HeII denominator is H; O02 rejects replacing it by He. |
| Full directional quotient | PASS | `delta-a=c*delta-N+N*delta-c`, `delta-R=delta-e+sum(delta-a)`; quotient/product rules give the written JVP. The cross-node sign is negative for a positive other-node perturbation at fixed c,J,e. |
| Totals and forcing dependence | PASS for explicit partials | O03 retains variable totals/prefactors. Fixed totals are imposed only on chemistry directions. Kappa cancellation is a partial at fixed J/e/c/N; physical chain-rule terms remain. |
| Units and weights | PASS for source normalization | Extensive N already contains quadrature weight. J follows the CSV's per-second/per-cMpc^3 normalization and source box convention; TUBE_INPUT_STATUS states that convention. No second weight or per-atom divide was inserted. |
| Photon normalization and l1 bound | PASS exact-real | `sum(j_aug)=J`, `sum(delta-j_aug)=delta-J`; induced l1 norm of `I-p*1^T` is `max_j 2(1-p_j)<=2`. This is not an energy or closed photon-evolution theorem. |
| Photo-event connection | PASS static source correspondence | `physical_trial.photo_fields` sums groups; event source inserts only the photo pieces of F10,F32,F43. Population sensitivity requires each actual stage's b, denominator, and flux weights. |
| Boundary / positivity | PASS on restricted domain | Positive N,kappa,R; nonnegative c,J,e; moving structural zeros excluded. Kappa=0 and one-sided moving-zero derivatives are not admitted by this candidate. |
| Uniform physical tube | NOT_TESTED / UNKNOWN | Real saved endpoint enclosure found; complete source-input state/time/forcing-direction tube not established. See file/field table. |
| Machine source and other physics | NOT_TESTED | Binary64 residual corrections, subgrid node allocation, OTS/atomic derivatives, coupled thermal bound and exact-flow rho are outside this validation. |

## 2. PHYS-MATH-CODE

| Item | Status | Evidence / limit |
|---|---|---|
| Candidate and run identity | PASS | Candidate commit `12d64833419651a532451ad4c9a180aa65a0a70b`, tree `93f34e2c869e888a0f78bd67b53d905c74e83710`; two Python blobs in SOURCE_BINDINGS. Parent `9651959...` is context, not the tested candidate. |
| Permitted execution | PASS | One invocation of requested Python command, installed /usr/bin/python3 3.12.3; exit 0, no timeout. Raw stderr contains all 10 outcomes. |
| Reference separation | PASS for this fixture | Dual reference differentiates two normalizations and does not call the reduced JVP. O04 varies kappa in that reference; O05 rejects the frozen-R mutant. This is algorithmic reference separation, not reviewer independence. |
| Exact arithmetic and assertions | PASS | Fraction inputs, exact equality checks, domain rejection tests and norm inequality. No tolerance, skip, assertion, physical formula or code change was made. |
| Actual O01--O10 | PASS 10/10 | O01 primal; O02 HeII/H; O03 coefficient/totals; O04 dual JVP; O05 global feedback; O06 conservation; O07 zeros; O08 rejections; O09 bound/scaling; O10 opacity/group additivity. |
| Imports and scope | PASS by static inspection | Candidate imports only standard library; tests import standard library plus local owner_current_reference. No production/NumPy/JAX module, old suite, native ABI, workflow or canonical interval was invoked. |
| Prior runtime failures | PRESERVED, not mathematical RED | Original WORK_UNIT records pre-process ClientError / pre-kernel MCP 404. They are not failed assertions. Current stdout/stderr and exit are separate evidence. |
| binary64 / rounding parity | NOT_TESTED | Source `_condition:84--101` and `_allocate:104--119` include argmax residual corrections. Exact-real identities do not validate those machine operations or interval rounding. |

Finite conclusion: the unchanged source-bound exact-real resolved-owner JVP
reference passed the ten synthetic rational obligations. No defect requiring a
candidate edit was observed. These tests are neither exhaustive proof nor the
Rust-first numerical gate, and establish no production PASS.
