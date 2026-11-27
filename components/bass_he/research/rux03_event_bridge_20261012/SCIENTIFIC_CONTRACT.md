# HERE_RUX03_EVENT_BRIDGE_02 — scientific change contract

Date: 2026-10-12. Owner: BASS_HE supplier contract, implemented in the existing
rei_bianchi conditional production consumer. Model/harness: GPT-6 Astra,
physmath research/coding v4.0.0 (canonical bytes already verified).

## Observable outcome and original motivation

Expose a typed primitive Case A event bundle and make the selected production
RHS consume it to generate photon loss, species/electron sources, thermal,
binding, and escaped energy. This closes an event-consumption seam needed by
the preceding helium recombination-transfer supplier contract. The existing
production path already composes these processes; this work does not claim
its first integration. A one-channel perturbation must demonstrate exactly
one consumption, because conservative events duplicated twice still conserve
charge and energy.

## Source authority

- BASS_HE PR29: `1d9794b4de07eaa165631b984b4a7c1030671ae6`.
- Receiver production PR97: `1400093cdd121d8e6adb51ffeb360102a48653bf`,
  tree `b2c2ec7dedced03d618d50da36dbb2982401f397`.
- PR101 clean-build receipt repair is already merged into that PR97 head.
- PR83 remains a different owner/planning branch; this implementation will be
  proposed as an isolated draft based on PR97, not silently copied into PR83.
- Retained input IDs and numerical conventions are the existing
  SourceBoundConditional / source_bound_interval.py contract.

## Protected physics and conventions

Warm FT03/Hui–Gnedin rate/moment provider, Case A escape, primary-only external
photons, CR/RCT/HH OFF. T domain 30000..110000 K, Verner domain <=50000 eV,
and the distinct binding energies versus cross-section cutoffs are unchanged.
No recombination photon count/spectrum is invented. The fixed production API
selects the existing provider. The internal injected test provider is a
manufactured derivative check and is not an admitted physical provider.

All primitive event rates are proper cm^-3 s^-1; thermal/captured/absorbed
powers are proper erg cm^-3 s^-1. The existing AXI boundary converts number
sources by 10^6 and powers by 0.1 to SI. Photon state remains N=a_rel^3 n;
the external source, redshift, shear work, stage background and geometry
equations retain their existing ownership.

## Small coherent change

1. Preserve and expose the already computed RR/DR captured kinetic powers in
   Ft03Rhs; do not substitute average energies for those moments.
2. Route production thermal and node photo events through one owned Case A
   bundle into a ledger; remove consumption of the old aggregate atomic
   thermal/escape outputs at this call site.
3. Keep RHS protocol shape and default numerical semantics. Add a read-only
   EVENTS diagnostic response from the same detailed production evaluation.
4. Test the actual provider seam with an independently specified HeIII RR
   perturbation and the existing affected regression/domain fixtures.

## Acceptance declared before candidate execution

| Requirement | Evidence | Criterion |
|---|---|---|
| Actual consumption | Inject one HeIII RR delta and its kinetic power into internal provider; observe actual AXI source/RHS difference | one delta in each stoichiometric and energy term; unchanged photons/external power; normalized error <=2e-12 |
| Default preserved | Existing affected Rust conditional and FT03 tests | original test thresholds, no relaxation |
| Primitive event/moment agreement | Independent Decimal60 direct equations at the retained initial stage, no candidate import | nonzero component relative error <=3e-11 |
| Cancellation-sensitive net/source/energy | Same independent reference | absolute error divided by sum of gross event or energy magnitudes <=3e-11, not tiny-net relative error |
| Invariants | Separate H nuclei, He nuclei, charge, photon number and energy | normalized residual <=1e-12 at probe stages; existing interval ceiling unchanged |
| Stage/volume ownership | Existing volume/geometry/source tests and a noninitial affected call | original assertions; exact initial input bytes |
| Changed-path interval | Existing production Python runner with new binary, one selected warm interval 0..1e11 s / 2904 nodes / 17 epochs | existing 2e-6 comparison and 1e-9 ledger ceilings; no changes to solver tolerances or physical inputs |
| Runtime identity | Fresh clean committed native build, toolchain/flags/logs, source and binary hashes; existing prelaunch validator | exact source and binary match before native use |
| Independent decision | Separate reviewer after candidate and evidence freeze | no unresolved blocking finding in stated scope |

## Execution and stop rule

Local environment probe found no rustc/cargo. A narrow branch-triggered CI
build/test job is used to obtain a source-bound binary; no NCP work unit.
Run primitive/stage probes before the single affected production interval.
Do not replay the previous eleven-history campaign, B1, PR113 screening or
unchanged P03A work. Preserve first failures and repairs. No optional new
precision campaign after the above evidence resolves the changed-path risks.
Publish source/evidence and draft PRs under the user's existing research-loop
authorization. No merge, no messages to third parties.

## Claim ceiling

The promotable claim is a typed, source-bound Case A event consumer in the
selected conditional production path plus its changed-path numerical evidence.
This does not by itself complete the entire receiver RUX03 owner node, diffuse
transport, coupled OTS, cold histories, cosmological physical admission, or a
continuum error certificate.
