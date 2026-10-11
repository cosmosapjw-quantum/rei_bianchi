# P0: complete atomic checkpoint generations

**Scope: implemented reusable I/O capability and new manufactured recovery fixture. Q1B production binding is absent.** No native/provider call, previous RUN002/EVENT003/Q0 replay, or new physical Q1B evolution is performed by these files.

The C08R1 interruption preserved a last state but not its complete history and accepted extrema. That state is not upgraded into a recoverable full-history checkpoint here. Existing Q1A outputs remain unchanged.

## API and saved contract

```python
path = publish_generation(root, generation, arrays, metadata,
                          expected_identity, physical_validator)
snapshot = load_generation(root, generation, expected_identity,
                           physical_validator,
                           expected_manifest_sha256=trusted_manifest_sha256)
```

`generation` is an integer from 0 through 99,999,999. Existing generations cannot be replaced. `discover_generations(root)` lists only structurally complete, hash-consistent generations; it is not a physical validation or permission decision. The caller chooses a generation, binds its expected identities, and always invokes `load_generation` before restarting.

Every generation contains exactly four files: `arrays.npz`, `metadata.json`, `identity.json`, `manifest.json`. The NPZ is float64 numeric data and loads with `allow_pickle=False`. The manifest hashes and sizes its three data members. An external receipt can pin the manifest SHA-256; the optional `expected_manifest_sha256` argument enforces that pin on load. Without an external pin, self-consistency is not original-byte authenticity. The manifest explicitly says scientific admission is false and integrator internal state is not saved.

Required arrays are:

| Array | Meaning |
|---|---|
| `state` | Full accepted state at a natural segment boundary, including counters |
| `scales` | Positive state scaling factors |
| `counter_origins` | Initial counter values, verified against the first history row |
| `prefix_clock`, `prefix_state` | Complete common-epoch prefix, with every scheduled sample through the accepted clock |
| `scheduled_clock`, `segment_edges` | Full future/past sampling schedule and immutable event boundaries |
| `accepted_min`, `accepted_max` | Carried extrema over all accepted states, including those between saved epochs |

Metadata declares field names/units, counter indices, current clock, completed/next segment indices and bounds, accepted-domain flags, number/energy ledger maxima and normalization origins, restart kind and physical-binding scope. Identity records require SHA-256 bindings for source, grid, binary, control, physics contract, and physical-validator source file. The caller must obtain authoritative bindings; arbitrary strings that have hash syntax do not establish scientific provenance.

Generic checks enforce finite shapes and values, positive scales, strictly ordered complete-prefix clocks, exact natural-boundary correspondence, endpoint-state equality when sampled, counter-origin equality, enclosing extrema, domain flags, and finite nonnegative carried ledger maxima. A **caller-selected, source-bound physical-validator callback is mandatory on both publish and load**. It must validate domain and ledgers against the actual production definitions, including any data/control configuration beyond the generic schema. Saved flags or a hash-correct manifest do not replace that callback. The supplied callback binds only the manufactured fixture, explicitly rejects a production-binding label, and cannot authorize a physical run.

## Publication and restart semantics

1. The solver owner pauses at a natural segment boundary and supplies an internally consistent snapshot. Concurrent copying from a moving solver is not made atomic by this library.
2. Validation precedes writing. Files are created in a unique `.tmp-gen-*` directory, flushed and `fsync`ed. The directory is `fsync`ed.
3. Linux `renameat2(RENAME_NOREPLACE)` atomically publishes `gen-########`. Unsupported platforms fail instead of weakening create-only behavior. The parent directory is then `fsync`ed; newly created root components are also synchronized.
4. Temporary/torn directories are excluded from discovery; unexpected I/O failures can leave them for diagnosis. Readers recheck hashes, expected identities, prefix consistency, and the physical callback.

This is local-filesystem publication, conditional on filesystem/device `fsync` and rename guarantees. It does not test power-loss behavior or provide a remote backup. Remote upload acknowledgements, upload verification, downloaded-byte restoration, and scientific acceptance remain separate facts. If parent `fsync` fails after rename, an exception is reported; the visible generation must be inspected, not overwritten or assumed durable.

Restart means **a fresh BDF initialization at the next natural segment** using restored state, original scales/counter origins, carried histories/extrema/ledgers, and all frozen controls. Internal BDF order, difference table, Newton/LU state, and dense-output object are not restored. Restarting at an arbitrary interior step is unsupported. This module starts no solver itself.

## New manufactured recovery experiment

The dimensionless fixture is

\[
\dot N=s_N-kN,\qquad \dot U=s_E-(k+\lambda)U,
\]

with positive constant source, absorption and expansion-work counters. Its independently written closed form uses exponential relaxation. Both uninterrupted and split paths start fresh SciPy BDF instances at the same four natural boundaries. The split route publishes and reloads at `t=0.5`, then proceeds with the exact restored prefix and state. It compares complete state/prefix/extrema and all metadata, plus the analytic history and number/energy ledgers. This demonstrates the declared fresh-segment restart contract; it does not demonstrate arbitrary internal-BDF restoration or native Q1B binding.

Run the bounded tests with:

```bash
python3 -m unittest discover -s research/accel02_20261011/q1b/checkpoint -p 'test_*.py' -v
```

The tests were written before implementation; the expected import failure is preserved as `evidence/CHECKPOINT_TESTS_FIRST_FAILURE.log`. Cases cover exact complete-generation restoration, corruption, missing/torn members, stale provider identity, absent validator, mismatched prefix/boundary/counter origins, create-only collisions, malformed manifests, callback rejection, and the new split experiment. Final actual results and retained fixture generations are in `evidence/CHECKPOINT_VALIDATION.json` and `evidence/CHECKPOINT_GENERATIONS/`.

## Remaining production gate

Before a long physical run, the actual Q1B driver must bind the source/grid/native binary/control and scientific-contract identities; implement a production domain/ledger validator; collect accepted extrema and ledger maxima at all required states; invoke the writer from a synchronized natural-boundary hook; restore through the reader; and demonstrate a bounded test of that exact hook. Remote durable receipts must be confirmed separately. These integration and review obligations remain open.
