# Explicit physical cutoff endpoint

The unchanged generic API evaluates E_end=E0 exp(-h) and fails closed when the rounded result is below the tracked/active-species cutoff. The reproduced 14 eV ->13.6 eV example with h=ln(14/13.6) yields 13.5999999999999979 eV and is rejected; see GENERIC_BEFORE.stdout. The generic guard remains unchanged.

The separate `characteristic_to_cutoff(initial, q, rates, E0, cutoff)` accepts only the exact declared cutoff values 13.6, 24.59, 54.42 eV. It requires E0>=cutoff and rejects nonzero rates for channels whose cutoff is higher than the chosen endpoint. A caller must therefore split a characteristic at each active physical event and supply the rates of that segment. This function does not determine or move the topological event.

The mathematical width h=ln(E0/cutoff) is evaluated as ln1p((E0-cutoff)/cutoff). This avoids premature division rounding for a one-ULP positive interval next to the cutoff. No epsilon, clipping or nextafter is used in the implementation. `nextafter` appears only in the independent oracle's test fixture generation.

Returned `AnchoredCharacteristic` fields:

- h: admitted computed segment width;
- characteristic: independently computed positive owners and omitted-addend diagnostics;
- unanchored_endpoint_ev: the binary64 E0 exp(-h) round trip;
- energy_anchor_roundtrip_relative: (unanchored_endpoint_ev-cutoff)/cutoff, an observed diagnostic, not a rigorous error bound.

The endpoint energy owner is explicitly U=epsilon_eV*cutoff*N. Initial energy, absorption energy, source energy and redshift work retain the analytic formulas at the returned h. Thus an unavoidable floating geometry discrepancy is visible in the energy identity; it is never assigned to another owner to make the residual vanish. For the actual fixture matrix, the high precision analytic energy discrepancy caused by this endpoint anchor is <=5.1626561e-18 relative to initial+source energy. This is a measured finite-matrix result, not an exact-bit conservation certificate.

Validation executed after the loop1 source was frozen separately: 14 native tests (the 10 affected original tests and 4 new cutoff tests), 48 independent Decimal160 fixtures, 1248 owner checks including export, 604 exact zero owners. The largest positive owner relative error is 8.3312057e-15 against the unchanged 3e-12 target. The largest computed h relative error against Decimal ln(E0/cutoff) is 8.0210158e-17, below the separately fixed 3e-15 geometry criterion. Equal endpoints, one-ULP intervals above every cutoff, very opaque positive tails, source-only and exact-empty states are included.

The reported binary64 endpoint round-trip discrepancy reaches 3.9169941e-16; it is larger than the analytic energy discrepancy and represents a different operation. Both are retained. Do not confuse these diagnostics with coupled gas, spectral quadrature, four-step or long-history admission.

Reproduce from crate root:

    rustc --edition 2021 --test src/tail.rs -o target/tail_tests
    target/tail_tests
    rustc --edition 2021 scripts/tail_anchor_probe.rs -o target/tail_anchor_probe
    python scripts/check_tail_anchor.py --probe target/tail_anchor_probe --output evidence/tail-anchor-replay
