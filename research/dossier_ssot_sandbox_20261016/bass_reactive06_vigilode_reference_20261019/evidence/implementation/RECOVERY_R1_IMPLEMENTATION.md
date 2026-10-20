# BR06 implementation recovery R1

This is a recovery revision following the workspace-pruning interruption. The
two central V2 files have been restored with their original SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `br06/src/reference.rs` | `9c04870c09bd16550a431a2b8eba4ce2f8d4f3fa45d9de0eb407c6b1d94eb1fc` |
| `br06/tests/reference_tests.rs` | `1b34b567c415899e5f1bdd290b82a57ba9cec7cffab9b6f5f93859e743bfab78` |

The other eight source/build files are reconstructed or newly resolved R1
files. Their identity and current verification must be read from the new R1
manifest and logs. Historical V1/V2 execution claims were not recovered as raw
receipts and are not current verification evidence.

## Input and physical ownership

`NativeFixture::load(root, case)` binds the actual recorded first BR05 step:
`t0=0`, `tm=2.5e11 s`, `t1=5e11 s`. It reads the exact restored first-step
source and gas CSVs. Both signed BASS cases use the same recorded minus-case
midpoint comoving gas inventory. At a path time, each midpoint opacity is
scaled by `V_recorded_mid/V(t)`, preserving all four competing channels.
The unchanged parent owns Verner cross sections, the specified manufactured
D binding threshold, MD14/BB50k source cells, and the BASS clock and geometry.

The source templates retain all 384 original spectral/angular labels. Every
quadrature birth retains its own time, geometry, direction, energy and number.
Source amplitude follows the owner at the actual birth geometry. Reflection
reuse in the byte-recovered path core is a computation cache; each labeled
birth still has its own exported row. The independent positive source-Gauss
alternative uses the parent's same graded age panels, with its degree
controlled separately from path-opacity and absorption-event quadratures.

This stand-alone, opt-in reference does not call a new nonlinear gas step or
modify the parent's CX half-flows or four-corner controller. Unchanged parent
regression validation is owned by the root recovery task.

## CLI

Build from `br06/` with the pinned toolchain and vendored registry:

```sh
cargo build --release --locked --offline --bin br06_reference
```

The binary accepts exactly these forms:

```text
br06_reference fixture CASE export OUT
br06_reference moments CASE export OUT
br06_reference run CASE METHOD R BIRTH_DEGREE SLABS OPACITY_DEGREE EVENT_DEGREE SPECTRUM TEMPLATE_LIMIT OUT
```

`CASE` is `SIGNED_MINUS` or `SIGNED_PLUS`. `METHOD` is `fitted` or `gauss`.
`SPECTRUM` is `original` or `split`. `TEMPLATE_LIMIT=0` selects all templates;
a positive limit is an explicitly identified prefix smoke test. The fitted
method obtains its rule directly from the unchanged parent; `BIRTH_DEGREE`
is used only by the Gauss method. Source scale is fixed to one in the CLI.
The public API also tests exact zero source and rejects negative source.

For example, a one-template smoke run is:

```sh
br06_reference run SIGNED_MINUS fitted 4 2 4 4 8 original 1 smoke_output
```

The primary run writes `BIRTHS.csv`, `PATH_FLAGS.csv`, `TEMPLATES_RESULT.csv`,
`SUMMARY.csv`, and `DIAGNOSTICS.json`. The fixture export writes the actual
source template and gas fields plus owner geometry probes. Output quantities
and physical units are named in their CSV headers. The `wall_s` column in
`SUMMARY.csv` is a measured execution field and is excluded from numerical
restore parity.

## VigilODE application

The R1 adapter calls the exact pinned VigilODE moment kernel at local optical
depth at most one and composes the complete normalized age integral using
positive dyadic identities. It keeps directed intervals and a typed width
refusal. The native diagnostic uses the actual 48 original source energies
and frozen recorded gas opacity. It exports the normalized moments
`J00`, `J10`, and `J20`, constant-source number/age intervals, and an interval
for positive endpoint-linear source interpolation. The eight directions are
summed only for this scalar diagnostic.

The separate `actual_source_gl8` and `actual_source_gl16` columns integrate
the actual MD14 source amplitude on the graded birth panels, at the actual
birth geometry and frozen scalar opacity. Comparing these with the endpoint
interpolant measures source interpolation error. The scalar interval does not
enclose the variable-geometry transfer operator or the interpolation error.

## Failure semantics

Invalid negative/nonfinite populations and source fields yield
`INPUT_REJECTED`; sample work exhaustion yields `REFERENCE_WORK_LIMIT`.
Inherited `Cx(WorkLimit)` maps to `CX_WORK_LIMIT` and remains distinct from
both. Representation collapse maps to `REPRESENTATION_LIMIT`; a rejected
scalar certificate maps to `VIGILODE_WIDTH_REFUSAL`. I/O and build problems
remain environment or input-dependency failures, with actual attempt logs.

The exact V2 path core separately reports positive quantities that round to
zero: survival, integrated opacity, absorption, individual species and heat.
Its thin-opacity route preserves representable subnormal competition events
and integrates geometry work in physical time. Final outputs expose the
maximum inverse optical-depth residual. Accuracy claims require the measured
native refinements and independent reference comparisons; they are not a
universal event-time bound for arbitrary `PathModel` implementations.

## Recovery validation

At source-checkpoint creation, current wrapper tests and scientific runs were
not yet executed. New logs and the final manifest supersede that execution
status while preserving the earlier candidate checkpoint. No previous
workspace's PASS result is inherited from a message alone.
