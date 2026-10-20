# BR06 recovery R1 implementation closeout

## Frozen deliverable

The final R1 implementation is frozen. Its ten source/build files and separate
portable Cargo bootstrap config are identified by `SOURCE_IDENTITY_FINAL.json`
(SHA-256 `f70901363e1901e71b6d2933dfa6080c9de9af8daa4e35178be77d1fcfab9402`).
The release executable SHA-256 is
`495cefac0f5bb5412f44d9ae15880856ff27cd3e92d7b594132cf8fb7b84e853`.

The complete source-and-current-verification checkpoint is
`BR06_RECOVERY_R1_FINAL_SOURCE_AND_VERIFICATION.tar.gz`, 146,183 bytes,
SHA-256 `5c8e649bfc47f0f6565203f6feee3c1493fa8576d7bf079848a850bba402c75f`.
The root task owns its durable-save receipt, fresh restore, full-source matrix,
and final publication. This closeout does not assert a GitHub, Drive or Dropbox
upload acknowledgement.

The original V2 transport core and original twelve-test file were recovered
byte for byte. The remaining eight source/build files are explicit R1
reconstructions or newly resolved build inputs. Previous numerical execution
receipts lost in pruning are not inherited.

## Current author checks

`AUTHOR_VERIFICATION_R1_FINAL.json` records fresh Rust 1.94.1 executions:

| Check | Current result |
| --- | --- |
| New Rust tests, release, locked and offline | 16 passed, 0 failed |
| Strict Clippy, all targets, locked and offline | Passed |
| Scoped rustfmt on the six reconstructed Rust wrapper modules | Passed |
| Actual BASS minus and plus fixture export | Both completed |
| Native VigilODE scalar diagnostic | 48 rows completed |
| One-template fitted-r4 smoke | 42 distinct labeled births completed |
| Admission-check repair parity | 12 files byte-identical; all fields of the thirteenth identical except measured `SUMMARY.wall_s` |

The smoke survivor count is `1.44838639093425760e-11` reference-comoving
photons/m^3. Its photon-number residual is `-2.06795153138256919e-25`, and its
independently checked energy residual is `1.19882146851273522e-35 J` in the same
reference-comoving volume. This is a declared one-template smoke, not a
full-source result or an accuracy admission.

The four newly reconstructed-module tests comprise the three scalar VigilODE
adapter tests and one actual malformed native-source CSV test. The twelve
byte-recovered path tests exercise constant-opacity source integrals,
competition, zero opacity/source, thick and subnormal limits, BASS signed
threshold exits, source/geometry provenance, refinement, and typed refusals.
The root task owns the freshly executed 233 unchanged-parent tests and their
strict Clippy receipt; they were not redundantly rerun by this implementation
agent.

## Bounded input-admission repair

The R1 fixture initially validated every row but did not require that all
spectral/angular pairs were present exactly once. A duplicate valid row with
an otherwise sequential template id could omit one native source population.
The final fixture requires `spectral_index=id/8` and `angular_index=id%8` for
the locked 384-template source. A test replaces one real CSV row with a
duplicate while retaining its sequential id and verifies the typed rejection.

This changes admission only. `SOURCE_COMPLETENESS_PATCH_PARITY_R1.json`
records exact valid-input parity for fixture, moment and smoke outputs. The
transport core, original tests, parent owners and numerical operation order
remain unchanged.

## Recovery failures and disposition

| Evidence | Classification and disposition |
| --- | --- |
| `GENERATE_LOCKFILE.log`, exit 101 | Environment/network: the proxy on port 8889 was unavailable. Root recovered pinned registry packages through the available approved network path and verified the vendor checksums. |
| `CARGO_CHECK_R1_ATTEMPT1.log`, exit 101 | Bootstrap configuration: the registry directory initially had one extra parent traversal. Corrected to `../vendor/registry`. |
| `CARGO_CHECK_R1_ATTEMPT2.log`, exit 101 | Missing dependency input: the selected exact VigilODE snapshot lacked an included coefficient fixture. Reviewer restored all fourteen fixture blobs from the exact pin, without changing upstream source. |
| First smoke parity assertion | The comparison initially included measured wall time. Inspection showed only `SUMMARY.wall_s` differed. The final receipt explicitly records that sole exclusion; numerical/source/control fields match exactly. |

The prior V1/V2 conversation also reports an earlier disk-full build attempt
and the later pruning interruption that removed BR06 raw outputs before a
successful BR06 publication acknowledgement. Their deleted raw logs are
historical transcript provenance, not newly restored evidence. The current
failure receipts above are actual retained files.

## API and remaining work

`RECOVERY_R1_IMPLEMENTATION.md` supplies the exact CLI and ownership contract.
`reference::integrate_path`, `reference::emit_births` and `reference::run`
remain the recovered V2 API. A positive template limit in the CLI denotes a
prefix smoke; zero selects all templates. Birth refinement/degree, opacity
degree, event degree, path subdivisions and spectrum are separate controls.

The final source files require no more edits. Root is running the nine-case
full-source R1 matrix and owns scientific acceptance and fresh restoration.
The independent reviewer is binding the reconstructed 22-case thin-limit
probe to the final rlib; its new result is separate from the lost historical
probe. The theory agent owns independent scalar and variable-geometry
reference audits.

## Skill context

This recovery reused the authorized bounded BR06 objective and applied the
available `physmath-research-loop` coding and evidence/handoff policies:
resume from verified byte identities, distinguish source recovery from
execution, close the concrete bounded finding, and re-execute only affected
checks. The implementation agent read the current executor-provided skill
package and its `RESEARCH_POLICY.md`, `CODING_LOOP.md`, and
`EVIDENCE_AND_HANDOFF.md`. The root task records the wider session's skill
version context.
