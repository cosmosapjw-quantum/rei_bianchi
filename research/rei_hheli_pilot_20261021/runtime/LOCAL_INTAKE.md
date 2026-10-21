# New H/He/Li pilot: current runtime and local-source intake

## Boundary

This is a new task, distinct from completed D9. The current worker completed only runtime probes, read-only repository/source intake and evidence assembly. No scientific pilot, rate evaluation, ODE/IVP integration, coefficient-table build, model import or moment calculation was run. D9's zero-new-IVP contract belongs to D9; it is not a prohibition on the new requested pilot. A new root/Astra scientific contract is still required before implementation or science execution.

Requested execution model: `gpt-6.1-sol high`; observed model identifier: `NOT_VISIBLE`. Current AGENTS tier excerpt is parent-bound to blob `429a5a13ee75b1222bc50627f8d5973d01dd21c4`: Astra owns framing/contracts/admission; this worker owns bounded mechanical implementation and evidence after the contract. No subagents were spawned.

## Current-turn probes

At 2026-10-21T14:55:13Z, the actual Python/NumPy/SciPy probe returned **PYTHON_PASS**: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0; 2×2 linear-solve residual 1.7763568394002505e-15, exit 0. Actual C++17 compile/run returned **CPP_PASS**: g++ 13.3.0, compile exit 0, execution exit 0, sqrt-square residual 4.44089e-16. Both were small capability probes, not scientific validation or benchmarks.

Observed affinity CPUs 0–8; cgroup CPU quota `800000 100000` (8 CPU equivalents), cgroup memory limit 8589934592 bytes, current use 686407680 bytes; host MemAvailable 9462000 KiB. Available scratch disk 23632130048 bytes. Load averages 1.0146484375 / 1.34423828125 / 1.6357421875, cgroup pids.current 64. These are current observations, not claims of exclusive resources.

The named owner home and `/home/cosmosapjw/.ssh/ncp_key` are absent by existence-only checks; key contents were never read. No DesktopCommander call/retry or remote-login attempt was made.

## Repository preservation

`REPOSITORY_STATE.json` records actual read-only Git probes. The current workroot, `rei_unified_20261021/repo`, and neighboring `36ad4bc67b35/rec_bianchi` are directories but are **not Git checkouts**: HEAD/branch/status queries exit 128. Thus the probe's legacy `local_checkout_exists=true` means directory existence only.

The neighboring `/workspace/scratch/39bb8df06b79/repos/BASS_HE` is an actual checkout: branch `research/he30-z2-continuation-20261021`, HEAD `4378220f0d303a993f943a20e163dd74bda562df`. At observation it had 91 tracked dirty rows (87 tracked deletions) and 31 untracked rows. No files, branch, index, dirty state or processes there were repaired, reset or changed. These neighboring sources are candidates for hash-bound reuse, not authority to mutate their repositories.

## Protocol identity reuse

The full 04/05/07/08 protocol texts were read earlier in this same session. Their actual bytes were hashed again this turn and match the prior receipt exactly; `PROTOCOL_IDENTITY_REUSE.json` records all four identities. Reused requirements: contract and actual path first; distinguish runtime smoke capability from scientific validation; targeted controls; PHYS-MATH then PHYS-MATH-CODE review; actual figure reading and semantic/print checks; bounded repair rather than completed-campaign repetition.

Previously read PhysMath Research Loop 1.3.0 SKILL.md, POLICY_INTEGRATION, STAGE_GUIDE_KO and CODING_LOOP remain the skill context used. Selected present scope is C1/C2 intake and C6 capability probes only.

## Local code inventory and coverage facts

`LOCAL_SOURCE_INVENTORY.json` records exact source paths, sizes, SHA256 and mechanically extracted API names. Several candidates are read-only source exports in neighboring scratch workspaces, with matching earlier upstream pin/blob metadata where available. No new remote verification of those neighboring source pins is claimed.

| Candidate | Observed implemented surface | Limit relevant to the new contract |
|---|---|---|
| `li_sandbox_inputs/raw/isotope_state.rs` | 13-number-state bookkeeping: neutron; H1 I/II; D I/II; T I/II; He3 I/II/III; He4 I/II/III; baryon/charge moments | Header explicitly supplies no physical rates or ICs. Its legacy H/He projection rejects non-H1/He4 populations. Bookkeeping is not a complete isotope kinetic network. |
| `li_sandbox_inputs/raw/lithium_rates.rs` | Explicit Li6/Li7 populations, four charges q=0..3 each; CI/RR/DR coefficients and number RHS; direct and fixed table providers | Li6/Li7 electronic coefficient equality requires explicit opt-in `ElementalElectronicEquality`; `IsotopeResolved` returns `MissingSource`. Header supplies no photo donor, thermal closure or abundances. Li8/Li9 have pending nuclear-decay/daughter closure. |
| `lithium_coefficients.json` and three primary row TXT files | Preserved Badnell RR/DR and Voronov CI rows; per-channel domains and units | Elemental source data, not isotope-resolved coefficients. Complete native bundle domain is `5/8.617385e-5 <= T <= 1e7 K`; channel-specific cold RR bounds differ. Do not silently broaden bounds. |
| `lithium_isotope_thresholds.json` | Primary spectroscopic Li6/Li7 neutral threshold donor | Explicitly marked not an active thermal-rate input; its existence does not turn elemental coefficients into isotope-specific coefficients. |
| `source_export/RUN13_FULL_NETWORK.rs` | Existing source-locked H/He/D finite-volume finite-time reference, one electron density/Cv, prescribed photon initial bins | The source header is H/He/D, not all H/D/T/He3/He4/Li states. It explicitly does not supply a cosmic emission history. |
| `source_export/FLRW_IGM_RATES.rs` | Selected low-temperature Grackle H1/He4 CI/RR/DR/thermal functions | Operational domain 1–1e6 K; floor/cap diagnostics retained; not a global empirical-support claim or FT03 admission. |
| `source_export/RUN19_LITHIUM.rs` | Binding around unchanged PR150 direct/table Li provider and number contribution | Explicitly does not assemble a full gas/energy equation; caller supplies proper electron density once. |
| `source_export/R9_LITHIUM_RATES.py` / `li_thermal_rates.py` | Source-derived selected ground-channel cross sections, finite thermal integrals, RR, scaled underflow-aware diagnostics | Requires its preserved Verner/rrfit inputs and selected channel contract; not itself a complete cosmic network. |
| `li_photo_driver.py` | Direct finite Li I photo response with frozen donor parameters | Its header states Li I response only; it must not be described as all-ion photo evolution. |
| `source_export/HE31_DONOR.py` | Content-pinned H/He electron table, PCHIP comoving electron number versus ln(a), prepared scalar path | A saved-history donor interface, not self-consistent new H/He/Li chemistry. |
| Existing B pilot adapter/vendor | Actual signed matter/radiation initial controls, canonical FV source and radiation hierarchy, completed z20→2 histories | Reusable geometry/source paths; no full primordial isotope network is implied. Preserve completed raw/receipt identities and do not rerun just to reproduce intake. |
| Neighbor `rec_rei_hheli.../code/geometry.py` | Existing research geometry implementation and provenance inputs | Only geometry/verification code was observed there at intake; no complete runnable H/He/Li network was established. Treat as candidate, not adopted implementation. |

The native Li q=3 terminal state is the missing Li IV entry noted by the parent from the illustration, and Li6 is explicitly represented. This observation is code inventory, not a new physical derivation. Species registry/abundances, isotope approximation policies, microphysical closure, source history, thermal/charge coupling, Sigma/Pi sweep and matter/radiation interaction must be frozen by the root.

## Immediate reusable runtime paths

1. Python/NumPy/SciPy are already executable. Existing Python donor functions and scalar coefficient formulas can be reused after exact source/closure mapping without a Rust bootstrap. This is an available path, not a benchmark-based speed claim.
2. g++ is already executable for a small native kernel or wrapper if the frozen contract needs one. No microphysics native binary was built or its API qualified in this intake.
3. Existing Rust source donors are readable, but crate dependency assembly/runtime availability was not established and no Rust install or Cargo campaign was attempted.
4. For later bounded parallel work, current effective quota is 8 CPUs and memory limit 8 GiB. Start with one inner BLAS/OpenMP thread per process and preserve unrelated jobs; choose an actual worker/resource cap under the root's execution contract.

Project source ZIP 12 and ZIP 17 were inspected by TOC only. ZIP 12 has no matching microphysics paths. ZIP 17's apparent atomic matches are vendored thread/synchronization primitives, not this physical network. No large archive was unpacked.

## Exact next action

Return these source/coverage facts to the root, then wait for the new H/He/Li scientific/execution contract. Do not implement rates, invent isotope physics, run a new sweep or apply the old D9 zero-IVP rule to this distinct task by default.
