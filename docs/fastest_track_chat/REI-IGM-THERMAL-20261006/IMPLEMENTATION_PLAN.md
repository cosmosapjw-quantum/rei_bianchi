# Low-temperature H/He point provider and event/thermal RHS

Bounded additive unit, 2026-10-06. No integrator, source history, interval certificate, observational calibration, commit or push. Preserve foundation and FT03/S0 bytes except additive lib exports.

## Frozen model and channel map

Case A, C=1, primary-only. Operational 1 <= T/K <= 1e6, NOT a claim of empirical fit accuracy. Source Grackle 3.4.1 af7939494ce65007887ada7b98d1813df6843346 `rate_functions.c`, exact selected units=1 bodies with original constants. Independent upstream-C reference is separate from Rust transcription.

- CI HI/HeI/HeII: k1/k3/k5; events ne*n_absorber*k; thermal sink chi_i*events using existing HHe binding/eV owner. Do NOT also add Grackle ciHI/ciHeI/ciHeII approximate-threshold cooling.
- RR HII/HeII/HeIII: k2, radiative summand of k4, k6; kinetic cooling reHII/reHeII1/reHeIII times ne*n_ion. Escape carries kinetic cooling + binding per recombination. Do NOT add FT03 derivative moments.
- HeII DR: other k4 summand only where T/11605 >0.8. reHeII2 used once in same branch; low-branch raw cooling is reported as excluded, because k4 has no matching DR event there. This explicit closure truncation preserves finite rates and reports the source residual rather than hiding it.
- CE: ceHI*ne*nHI, ceHeI*ne^2*nHeII (erg cm6/s coefficient), ceHeII*ne*nHeII. No species events; thermal energy goes to escape.
- Freefree brem*ne*(nHII+nHeII+4nHeIII), thermal to escape.
- Source floors tiny=1e-20 in CI and exp[-min(ln1e30,E/T)] caps retained and flagged. Numerical floor/cap contributions reported separately from totals.
- CMB signed Thomson transfer 4 sigmaT a_rad kB/(me*c)*ne*Tcmb^4*(Tcmb-T); separate equal/opposite reservoir, never mixed with nonnegative escape. Fundamental constants source audited.
- Optional external photo input Gamma[HI,HeI,HeII] s^-1 and heat per absorber erg/s, both finite nonnegative, heat=0 whenever Gamma=0. Photo event n_i Gamma_i owns binding; n_i heat_i owns thermal. Input radiation loss is their sum; this is externally prescribed point regression, not photon transport or source-driven history.
- RHS in proper time: fractions from events, electron derivative reconstructed by charge, dw/dt=-2Hw+Q/nH; dT/dt includes variable-particle term; density derivatives are chemical only, not expansion. Material binding+thermal, escape, external-photo input, signed CMB, and expansion-work close algebraically.

## TDD and verification

Write stubs and tests first, capture runtime assertion failures. Then minimal source-bound implementation. Tests: independent C parity including boundaries/caps; exact old guards unchanged; branch diagnostics; zero electron/species/He; density powers; species and charge; energy closure; CMB sign/equilibrium; EOS particle feedback; invalid/NaN/out-of-domain transactional no mutation. Strict checked products reject nonfinite or underflow of positive data; intentional source k1 exponential underflow to floor is documented.

Run full locked/offline cargo suite, scoped rustfmt, clippy classify existing warnings. Record commands, hashes, reference CSV, limits; independent review required before publishing.
