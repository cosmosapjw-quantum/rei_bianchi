# R6 phase-one read, exposure, and execution ledger

Unit: `rei_rr_mao_finite_temperature_enclosure_20261028`  
Actual reviewer task: `/root/rr_mao_native_reviewer`  
Host: `0e9a46d15332`; observed platform: `Linux 6.18.55 x86_64`.  
Working directory: `/workspace/scratch/cc0531120bc9`.

This ledger records text exposure separately from byte hashing. Hashing a file is not a semantic read of its scientific contents. Source-only means no new implementation/test/result evidence was admitted; it does not mean the original sources were stripped of historical evaluations.

## 1. Full and partial semantic reads

| Exact file | Lines read | Reason and boundary |
|---|---|---|
| `/workspace/scratch/cc0531120bc9/rei_post_dr_continuation_20261028/unit/THEORY_AND_CONTRACT.md` | 1–189, entire file | Required full author R5 proof, scope, source assumptions, controls, and contextual sentences. No section was redacted. |
| `/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/unit/source/atomic_coefficients.json` | 1–288, entire file | Required exact source coefficients and runtime domain. Also exposed the original photo/DR fields and historical LiI cross-section reference numbers. |
| `/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/unit/source/recombination_moments.py` | 1–153, entire file | Required RR definition and native rate-derivative closure context. Read as source text; no import or execution. |
| `/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/unit/source/thermal_sources.py` | 1–118, entire file | Required selected Mao formula, natural-log/eV convention, default constructor choice, kinetic-loss substitution, and separate binding-energy owner. Read as source text; no import or execution. |
| `/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/unit/intake/physics/source/mao2017_selected.json` | 1–453, entire file | Required all six selected Mao rows and mapping; original historical evaluations retained and exposed. |
| `/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/survey/physics/source/MAO_SOURCE_LOCK.json` | 1–22, entire file | Original source lock supplied by parent after the literal relocated lookup failed. Its selected SHA256 and raw-table SHA256/byte counts were checked mechanically. This was provenance, not a new test return. |
| `/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/survey/physics/source/mao2017_pars.dat` | 1–12; additionally lines 31, 32, 60; lines 1, 2, 3 re-read by selected-key `rg` | Original raw source parameters. Initial short read exposed rows for n=1,Z=1..12; source-key selection then read the six relevant rows. No other semantic text from this table was read. |

## 2. Explicit source-embedded and author-context exposure

The entire selected JSON was read, including its source statements at lines 2–6. The natural-log verification claim in line 3 was visible but was not independently reproduced. The “not a statistical uncertainty” statement in line 6 is part of the source metadata.

| Selected row | Fitted-residual field | Original source table values | Historical comparison/evaluation fields |
|---|---|---|---|
| `1:1` | line 21 | lines 22–63 | lines 64–80 |
| `2:1` | line 95 | lines 96–137 | lines 138–154 |
| `2:2` | line 169 | lines 170–211 | lines 212–228 |
| `3:1` | line 243 | lines 244–285 | lines 286–302 |
| `3:2` | line 317 | lines 318–359 | lines 360–376 |
| `3:3` | line 391 | lines 392–433 | lines 434–450 |

The last column includes `formula_vs_rounded_table_max_percent`, the pilot/contract comparison numbers, their locations, minimum derivative factors, and `f_at12000`. These values were not hidden, altered, recomputed, or promoted into current-unit results. They are not controller-selected anticipated defects. The raw parameter-table rows also carry their original residual-percentage column, which was exposed when those rows were read.

In the author proof, the following context was necessarily visible in the full read:

- Line 7: prior DR acceptance and pending figure/resource obligations.
- Line 11: pinned dependencies and census statement.
- Line 21: explanation of historical Mao evaluation exposure.
- Lines 160–176: author-proposed analytic controls and possible supplemental CAS checks, including examples concerning the lithium correction and c0 curvature.
- Lines 184–186: intended API, arithmetic/caching obligations, and anticipated numerical checks.
- Line 188: physical-scope nulls and original DAG counts.

These exposures mean this reviewer was not blind to the author's hypotheses or proposed controls. They do not supply actual implementation/test outcomes. No stated status/count was used as scientific acceptance evidence.

The full coefficient JSON also exposed original `LiI_partial.cross_section_reference_Mb` numbers at lines 116–126 and DR source fields at lines 218–280. Those were outside the RR/Mao proof target and were not treated as new test results.

## 3. Mechanical identities and reads

| File | Observed SHA256 |
|---|---|
| `unit/THEORY_AND_CONTRACT.md` in `rei_post_dr_continuation_20261028` | `9f18c1a5826881ff2f062036304e544515fd3a7baa58498f85795224ba529ead` |
| `unit/source/atomic_coefficients.json` in `rei_approved_continuation_20261028` | `38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc` |
| `unit/source/recombination_moments.py` in `rei_approved_continuation_20261028` | `5eb740518d04dcbf123125f3d73a85fa10b48bb3bad6577cdf81459d71a390b0` |
| `unit/source/thermal_sources.py` in `rei_approved_continuation_20261028` | `622bc85b21d819779d98ee2a7645f51deff9a91f7a423872dbe244f5378aa769` |
| `unit/intake/physics/source/mao2017_selected.json` in `rei_approved_continuation_20261028` | `34b5fb8dab049744faa0c6f734ce59f1c72b931b3cf2db298c01156f86d17803` |
| `survey/physics/source/MAO_SOURCE_LOCK.json` in `rei_approved_continuation_20261028` | `09257023bc18bc01133389aad3a9796e9dc2bfbc59c643ca9659e849776931b0` |
| `survey/physics/source/mao2017_selected.json` in `rei_approved_continuation_20261028` | `34b5fb8dab049744faa0c6f734ce59f1c72b931b3cf2db298c01156f86d17803` |
| `survey/physics/source/mao2017_pars.dat` in `rei_approved_continuation_20261028` | `a3c97fdf8101da6d33cc838f7fd4e142bcf3740c37b48d89e76c47ae91575d12` |
| `survey/physics/source/mao2017_calc.dat` in `rei_approved_continuation_20261028` | `bf7ad20e10ff7045fc83b4c4c4148132c291f315213c5fc7b00ae820c76aa58a` |

The coefficient file's Git blob was mechanically computed as `2eba600a9d7a7359ca55f566f1b841a363a3e5c7`. The original raw parameter and calculation tables had 22185 and 30600 bytes, respectively, matching their lock entries.

The preserved survey copy of `mao2017_selected.json` was hashed but not separately semantically re-read because its hash equals that of the full supplied copy already read. The full raw `mao2017_calc.dat` was hashed and sized only; its scientific contents were not read. These are deliberate not-read dispositions, not missing files.

## 4. Failed lookup and source-only follow-up

The following literal path was attempted with `nl -ba` and `sha256sum`:

`/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/unit/provenance/MAO_SOURCE_LOCK.json`

Both operations returned `No such file or directory`. No bytes were obtained. This exact lookup followed the `UNIT/'provenance/MAO_SOURCE_LOCK.json'` reference in the supplied native source.

The reviewer reported this limitation to the parent without requesting code/test results. The parent replied with the preserved original survey-source directory and named the original lock, selected JSON, and raw tables. The reviewer then performed the limited source reads and mechanical identity checks recorded above. No implementation, unit-result, CAS, or sibling-review evidence was supplied by that follow-up. The initial absence is retained in the record and is not rewritten as a successful first lookup.

After the first write of the phase-one conclusion and ledger, and before sealing their hashes, a second parent message announced availability of `newunit/code/rr_mao_enclosure.py` with SHA256 `1ecd1459f06853069162902ea839e9a513c1f807c68c0267b690cfb5323b7f09` and `newunit/deps/dr_interval_original.py` with SHA256 `be32fe17982ec9d1e9a6d506e37296d11cbe39fd6bc66690e6563ee62e2fb59c`. It requested static implementation review only after sealing phase one and stated that no unit execution outputs existed. Only these availability/path/hash facts were exposed before sealing. Neither implementation's contents, test source, wrappers, nor CAS/result contents were read. The provisional mathematical findings were already written; this paragraph records the subsequent metadata exposure honestly.

## 5. Deliberately unread categories

| Category | Disposition and reason |
|---|---|
| New unit implementation | Not opened, searched, imported, or executed before sealing. Assignment initially said implementation was being prepared; after the provisional report was first written, the parent announced its availability and hash. No tested-status inference made. |
| New test source and expected-result fixtures | Not opened or searched. Preserve source-only phase ordering. |
| New CAS output or numerical/oracle results | Not read or produced. Preserve source-only phase ordering. |
| Sibling review/status/handoff/census documents | Not opened or searched. No lateral acceptance or expected-defect exposure. |
| Prior-unit numerical results and plots | Not opened. Historical claims embedded in author/source text are separately recorded above. |
| `mao2017_calc.dat` contents | Not semantically read; only source-lock hash/size comparison was needed. |
| Remaining `mao2017_pars.dat` rows | Not semantically read beyond lines listed above; outside the six selected channels. |
| Runtime source-layout reconstruction | Not performed. The preserved-source definition was sufficient for the mathematical review. |
| Remote PR history and dependency commits | Not fetched. Their identities are stipulated context, not independently confirmed here. |
| Badnell RR page, Verner author page, Mao DOI/publication | Not retrieved during phase one. The fixed native/source-table definitions suffice for the scoped theorem; no broader literature/physical-fit validation is claimed. |
| Other project directories, agents, or credentials | Not enumerated or inspected. No need for the source-only task. |

## 6. Operation and resource disclosure

The scientific review consisted of textual source inspection and manual mathematical reasoning. Executed mechanical tools/commands were `pwd`, `hostname`, `uname -srm`, `wc -l`, `wc -c`, `nl -ba`, `sed` for an original table's short prefix, `rg -n` for original source-table keys, `sha256sum`, `git hash-object`, the clock tool, `mkdir -p` for the report directory, and `apply_patch` for the report/ledger. Subsequent mechanical readback/hashing of these review artifacts is permitted and belongs to preservation rather than scientific evaluation.

No scientific source execution, CAS, numerical Python/NumPy evaluation, tests, external communication, plotting, or external write occurred. This is a record of actions, not a claim that review consumed no resources. Total model compute, token use, host CPU time, tool dispatch, filesystem overhead, and scheduling latency were not measured and remain unknown.

First explicit clock observation was `2026-10-28 12:26:47 UTC`; a pre-report observation was `2026-10-28 12:29:38 UTC`. These observations do not establish task CPU time or total compute cost. File sealing will record its own later UTC timestamp.
