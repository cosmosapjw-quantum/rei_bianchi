# C10 split-step boundary checkpoint

`entry_checkpoint.py` binds the existing atomic create-only publication layer
to the new split map. Its claim is local checkpoint validation and boundary
restart. The manufactured experiment calls the actual new source-entry and
positive-absorption implementations, with fixed gas and immediate radiative
escape. It does not call the native gas provider or admit a cosmological run.

The only change to `../checkpoint/atomic_checkpoint.py` allows the explicit
`FRESH_SPLIT_STEP_AT_NATURAL_SEGMENT_BOUNDARY` restart kind alongside the
existing BDF kind. Unknown kinds still fail. The adapter itself requires the
split kind and never claims to save internal BDF/Newton state.

## Driver interface

```python
state = pack_entry_state(gas, N, U_eV, counters)
arrays, metadata = make_entry_snapshot(
    clocks=accepted_clocks, states=all_accepted_states,
    R=all_accepted_R, support=all_accepted_support,
    all_boundary_clocks=complete_frozen_boundary_sequence,
    nH_ref=nH0, nHe_ref=nHe0, scales=positive_fixed_scales,
    physical_binding='SOURCE_ENTRY_POSITIVE_STEP_V1')
identity = entry_identity(source=source_file, grid=grid_file,
    binary=native_binary, control=control_manifest,
    physics_contract=physics_contract_file)
path = write_entry_checkpoint(root, generation, arrays, metadata, identity)
restored = load_entry_checkpoint(root, generation, identity,
    expected_manifest_sha256=trusted_receipt_sha256)
```

Expected identities must come from the caller's authoritative frozen inputs.
Hashing arbitrary files establishes byte identity, not authority or physical
binding. A control manifest should pin all effective source/opacity/solver
modules and numerical controls. The actual native-driver hook needs its own
executed evidence; metadata expressly leaves this obligation open.

| Field | Shape / units |
|---|---|
| Packed state | `gas[4], N[n], U[n], counters[7]` |
| Gas | `xHII, xHeII, xHeIII, thermal eV/H` |
| N / U | photons/reference cm³; eV/reference cm³ |
| Counters | `Nsource,Nabs,Esource_eV,Eescape_eV,Wrad_eV,Wthermal_eV,ECMB_eV` |
| Complete history | `[accepted boundary, packed field]` |
| R / support | `[boundary,cell]`; `[boundary,cell,(q_left,q_right)]` |
| Scales | fixed positive `[packed field]`, with no state floors |

The current API covers a bounded sequence whose entire boundary schedule is
known. Every accepted step boundary must be present. It is not a checkpoint
contract for an adaptive full history with unrecorded accepted steps. Support
and R are retained at every saved boundary; a dormant cell may have b≤a only
with exactly zero paired N,U. Occupied cells must have a strictly interior
mean. Endpoint traces and hidden compensated low components are unsupported
and rejected rather than fabricated.

## Recomputed checks

The physical callback checks all saved boundaries: gas fractions, helium
simplex, 1–10⁶ K, N/U positivity and moment cone, complete support/R history,
exact carried extrema over that history, source/loss/work counter monotonicity,
and signed CMB exchange. It recomputes number and energy ledgers using the
unchanged chemical energies. The normalized tolerances remain 10⁻⁹, with
number normalized to initial nH and energy to the initial photon plus gas
thermal plus chemical energy. A 16-ulp allowance concerns only comparison to
the separately recorded ledger maximum; the actual 10⁻⁹ ledger gate is strict.

Saved flags cannot bypass validation. Missing prefix/counters, stale expected
identities, failed domains, missing support or underreported ledgers are
rejected on write or load. Generic atomic publication remains responsible for
file hashes, fsync, create-only rename and structural checks. Local success
does not establish remote backup or original-byte authenticity without an
external manifest pin.

## New evidence

`evidence/CHECKPOINT_ENTRY_VALIDATION.json` records seven distinct new test
cases and the actual execution logs, preserving the first missing-module
failure. The six-case run passed; the subsequent targeted run checked the new
loss-counter case and strengthened manufactured source/control bindings.
No old generic eight-test suite or completed physical campaign was replayed.

The final source-bound manufactured restart is retained in
`evidence/CHECKPOINT_ENTRY_BOUND_GENERATIONS/`, with fixture input manifests
in `CHECKPOINT_ENTRY_BINDINGS/`. It saves at t=0.5, restores with an external
manifest hash, advances to t=1, and obtains bitwise identical complete arrays,
prefix and extrema plus identical metadata to the uninterrupted new split
map. The first fixture generations remain preserved separately. This is
recovery equivalence of the same implementation, not an independent physical
oracle, gas-coupling test or continuum-time domain certificate.
