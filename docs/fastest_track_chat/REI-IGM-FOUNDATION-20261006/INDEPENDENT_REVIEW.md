# Independent review: first FLRW/HHe foundation unit

## Final verdict — confirmed for the bounded foundation unit

Contract: **confirmed** for analytic FLRW background, boundary-valid H/He state/EOS, explicit unit/count adapters and manufactured collisionless/adiabatic tracer. Quality: **confirmed** for this reviewed source and exercised checks, with no remaining blocking finding. The endpoint bug discovered independently was fixed and independently rechecked.

This is not a completed non-equilibrium IGM or reionization history: chemistry, cooling, emissivity, full integration, convergence/restart and observational/science validation remain outside this unit. Treat claims of their completion as unverified, not as transferred legacy certification.

Frozen contract: approved FLRW_HHe_IGM_DESIGN_KO.md, narrowed first-unit IMPLEMENTATION_PLAN.md. Repository base `2b6005fd9c88e5cb38213c5bb66baee7caf54583`. Initial read found only additive lib exports and four new scoped files; no existing scientific module changes. Independent reviewer did not modify product source/tests.

## Resolved finding (initial defect evidence retained)

- Axis: contract and quality; category: reliability; severity: medium; confidence: high.
- Location: `src/igm_background.rs:135,168–172` (initial reviewed bytes).
- Problem: a domain endpoint accepted through at_ln_a produces a redshift that the paired at_redshift API rejects because inverse-transcendental rounding moves ln(a) minutely below the strict domain bound.
- Evidence: independent scratch executable `reviewer_extra.rs`; `reviewer-extra.log`: 38/999 ordinary endpoint roundtrips rejected. At ln_a_min=-0.03, returned z=0.0304545339535169379 inverts to ln_a=-0.0300000000000000787. The original endpoint is valid. This is observable failure rather than a preference for error-message style.
- Follow-up: narrowly bounded representational endpoint handling and regression exercising both endpoints while still rejecting genuinely outside-domain redshifts. Implementer supplied exact returned-endpoint identity handling, with no tolerance band or general physical clipping. Fresh independent lower and nonzero upper endpoint checks now pass; resolved.

## Independent evidence so far

All commands run after `source /workspace/shared/rei-build-feasibility/env.sh`, from `repo/rust/rei_microphysics` unless noted.

1. `cargo test --locked --offline --test igm_foundation`: exit 0, `7 passed; 0 failed`, reviewer-targeted.log.
2. `cargo test --locked --offline`: exit 0; 149 passing tests in total, zero failures/ignored, reviewer-full-tests.log. Includes existing 142 plus 7 added tests; default suite does not constitute rerun of costly scientific campaigns.
3. `cargo run --locked --offline --example igm_foundation_probe`: exit 0, reviewer-probe.csv / reviewer-probe.log. Nine rows produced. A separate Python csv/math calculation checked H(a), nH/nHe normalization, TCMB, T~a^-2, E~a^-1, counts/H, absolute comoving/proper density, exact fixed fractions, ne and EOS energy at relative 1e-12; passed. No full-history inference.
4. Scratch Rust probe compiled directly with rustc against current crate: public IgmGasState mutations to NaN energy and an invalid He simplex are rejected by both eos and adiabatic_to. Lambda-dominated background with small positive baryonic matter agrees with constant H limit to 1e-12. Pure Lambda/pure radiation with zero matter are not admissible under required positive baryon density; that is consistent with contract.
5. Inspection confirms H0 units s^-1; critical density cgs; helium nucleon-mass approximation explicit; nonnegative Omegas and 0<Omega_b<=Omega_m; no normalization of flatness; configuration stored privately; EOS uses actual electron count and exact neutral/simplex boundaries; fractions acquire no density-dilution term; gas energy erg/H converted with existing eV owner; photon packet count uses nH0, separately from occupation; node conversion includes Mpc^3; GeometryBackground proper-time trait deliberately not implemented. Gas operations revalidate public state fields. No chemistry/rate evaluation enters this unit.
6. Existing test overflow/error cases cover NaN, infinities, nonpositive inputs, underflow/overflow, direction validation and zero-preserving photon conversions. The implementer additionally rejected a positive-subnormal EOS denominator before delegating to the legacy EOS; the new regression passes in the final independent suite.
7. Initial implementer red.log contains compiled behavioral assertion failures on valid configurations/states, not import failures. This is inspected historical evidence, not an independently reproduced historical checkout.

## Initial reviewed source SHA-256

- igm_background.rs: 981aaeee53f6c41338ca254ffd6bf10c7e712a9cbc31bddf2da7607dff33eeb1
- igm_state.rs: 1633d5de0fb2c4fc2eb43894b3ab27414d442a2043f3aff951f18814c5e7ea77
- igm_foundation.rs: 740fe0d90aad0742260411c4756bd452ea3460859fa87703ad386c94836784ae
- igm_foundation_probe.rs: 06d8485a6747974fb3ea971b5625818cd47433f1376c9e9f7e8c05c6b50f4899
- lib.rs: 0d0da53e20d815e0be20bc010110c09782d9898116f807e14324635f8addca2f

The initial hashes above preserve the defective-state evidence. Final reviewed bytes and checks follow; any later changed bytes invalidate source-bound results until rechecked.

## Final independent recheck (2026-10-06)

- `cargo test --locked --offline`: exit 0, **151 passed**, zero failures or ignored (142 existing + 9 foundation tests), `reviewer-final-tests.log`.
- Original scratch probe rebuilt against final crate: exit 0, **0/999 endpoint roundtrips rejected**, `reviewer-final-extra.log`. This is the same observable defect probe that rejected 38 endpoints before the fix.
- Expanded scratch probe `reviewer_final_extra.rs`, rustc-built against final crate: exit 0; additionally **999 nonzero upper endpoint roundtrips and genuinely outside-domain rejection** pass; public-state mutation checks and Lambda-dominated analytic limit pass. `reviewer-final-extra-expanded.log`.
- `cargo run --locked --offline --example igm_foundation_probe`: exit 0. `cmp reviewer-probe.csv reviewer-final-probe.csv`: exit 0, final CSV byte-identical to the separately formula-checked nine rows.
- `rustfmt --check src/igm_background.rs src/igm_state.rs tests/igm_foundation.rs examples/igm_foundation_probe.rs`: exit 0.
- `cargo clippy --locked --offline --all-targets`: exit 0, `reviewer-final-clippy.log`; warnings remain in unchanged legacy files, no igm diagnostics. Clippy exit 0 is not described as warning-free.
- Final scope inspection: existing product files unchanged except three additive lines in lib.rs; the only untracked additions are the two scoped modules, foundation test and tracer example. No commit, push, scientific gate promotion or production campaign is part of this delivery.
- Historical implementation red-green logs inspected: original stub valid-input assertion failures; coordinate and EOS-denominator regression red logs supplied. Independent reviewer reproduced endpoint failure before fix and pass after fix; did not reconstruct the historical initial-stub checkout.

## Final reviewed source SHA-256

- igm_background.rs: ebe5d4ba0a61133512cecfe50791794a50aa22132bcc5189170e5668cbf1871f
- igm_state.rs: 1651b00a517d67aaa71b38d3c69af6413570adfc38b591a3ed25284f039e0ae0
- igm_foundation.rs: dda2f3abb9de2fdd8a84fa2b666d46230cb4fc1ebf8751c79574b74487faf506
- igm_foundation_probe.rs: 06d8485a6747974fb3ea971b5625818cd47433f1376c9e9f7e8c05c6b50f4899
- lib.rs: 0d0da53e20d815e0be20bc010110c09782d9898116f807e14324635f8addca2f

## Claim boundaries and remaining evidence

Confirmed: formulas, accepted boundary states, explicit units, scoped adapters, manufactured tracer, default existing regression preservation, final scoped formatting/build checks. Rejected: initial claim of reliable coordinate endpoint roundtrip; resolved by final fix. Inconclusive/not tested: low-temperature rate-provider/source parity, cooling/Compton, absorption/source birth, coupled non-equilibrium history, independent time integration, scientific convergence/restart, observational applicability, interval certification and high-cost scientific campaigns. These are explicitly deferred features, not unexplained gaps in this first-unit verdict.

The remaining implementation plan should keep the next chemistry/cooling and integrator admissions separate. No additional product changes are requested by this review.

