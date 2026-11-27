# HE-ANG-CCC-EXCHANGE

Conditional source-convention arithmetic for equal-sharing CCC amplitudes, with
an already-normalized real TP Table I input. The physical HE-ANG provider stays
`SOURCE_INPUT_PENDING`; every public adapter result says
`physical_provider_admitted=false`.

The controlling definitions and scope are in `FROZEN_CONTRACT.json` and
`THEORY_KO.md`. `source/PRIMARY_SOURCES.json` contains bibliographic identities
and source-byte hashes. Source PDFs, full extracted text and screenshots are
excluded from this unit and all delivery archives.

## Record interface

`code/ccc_exchange.py` exposes the five contracted public functions. Each
admission input supplies `source_profile="CCC_RAW_EQUAL_SHARING"`, nonempty
`source_id`, `producer_family`, `kinematics_id`, `preparation_id`, `density_unit`
and `differential_measure`, integer `spin=0|1`, and an explicit boolean
`spin_weight_applied`. `outgoing_energies` has `kind="point_exact"`, a named
`unit`, and two exact decimal strings in `values`. Exact decimal equality is
required; finite-bin averages and near-equal energies are rejected.

Representations have these additional fields:

- `raw_amplitudes`: `a` and `b` as `[real,imaginary]`, unweighted, and
  `phase_provenance={source_id,common_convention,relative_phase_preserved:true}`.
  The pair is interpreted in its own declared common convention.
- `coherent_density`: a nonnegative finite `density`, preserved without a new
  normalization factor; `spin_weight_applied` determines whether averaging
  applies the corresponding unpolarized weight.
- `incoherent_intensities`: nonnegative finite `A,B`, unweighted. This route
  returns a phase range and `C=null`, never a reconstructed phase.

`spin_average` requires exactly one channel per spin with matching source,
producer, kinematics, preparation, exact outgoing energy, unit and measure.
Relative phase between the two spin channels is immaterial to their incoherent
mixture; each raw pair must independently preserve its relative phase.

Quadratics return `{mantissa,exponent,float,status}` with value
`mantissa*2**exponent`. `OVERFLOW` or `UNDERFLOW` retains this pair and sets
`float=null`; exact zero has status `ZERO`. Eta is null at zero raw intensity.
The implementation scales each component sum by its largest absolute component
before direct squaring, then combines squared terms at a common binary scale.
This additionally preserves the tested tiny coherent remainder after a large
orthogonal cancellation. Binary64 arithmetic is tested at the frozen scaled
5e-13 tolerance; endpoints are not directed-rounding interval certificates and
no universal arbitrary mixed-scale relative accuracy is claimed.

## Execution

Root's explicit task instruction authorizes execution after B1 dual-provider
backup acknowledgement. The bounded runner records that native authority and
source/code hashes; no extra authorization or attestation file is required.
It executes only the following new-unit children in order:

```
python -B code/run_bounded.py 01_tests
python -B code/run_bounded.py 02_source_analysis
python -B code/run_bounded.py 03_plot
```

Fresh caps are CPU8s/wall30s, memory512MiB and one thread. Planned child caps
are CPU2/wall5, CPU2/wall5 and CPU2/wall10. One diagnosed, explicitly
root-authorized repair may use CPU2/wall10 inside the same cumulative caps.
START, failures, raw stdout/stderr and measured overshoots are retained. An
unfinished START or a failure blocks ordinary continuation. Source/metadata
ambiguity returns to root. Old evidence is read-only reuse and is not rerun.

The first panel of the planned figure uses manufactured phase controls; the
second uses only actual published Table I / printed BRM ratios. Neither is a
full H ionization provider or a new CCC/BRM solver result.

## Actual publication and delivery

Science S is `63706d605ddfc5d313ca310b09b5fd54a4efdbf4`, published as draft,
unmerged PR95. Central observation C is
`d5aa6c94a77b5687052d3d6902d140e2df9ef798`, based on the concurrent CR-N5
receipt head `f3ff95c4ddbdc4279223929a777072ec4eace577`.
B2 preserves those exact snapshots: 278842 bytes, SHA256
`21303684dbb2a0bed96d368802c70093cd343ccd644c53710036f16712c881f0`, 72 members.
Both Drive and Dropbox completed upload and independent metadata-size readback;
actual receipts are in `delivery/`. No independent remote SHA256 was supplied.

The 20 stage rows are COMPLETE_SCOPED in this delivery metadata commit, whose
self-identity is CURRENT_FILE_COMMIT. The final user delivery report awaits actual
D and central E publication/readback plus the B3 supplement's dual ACK. Science
code, inputs, numerical outputs, figures, reviews and raw runs are unchanged from
S; the initial14 methods plus one targeted C9-01 reserve remain reused evidence.
Complete end-to-end CPU accounting remains known-plus-unknown, with
end_to_end_cpu_cap_established=false. Physical HE-ANG stays SOURCE_INPUT_PENDING.
