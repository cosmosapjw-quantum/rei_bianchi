# Independent low-temperature point reference

Grackle 3.4.1 commit af7939494ce65007887ada7b98d1813df6843346:
https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/rate_functions.c

`grackle_literal_reference.c` contains mechanically extracted, unmodified selected function bodies. The exact pinned `grackle_macros.h`, `phys_constants.h` and upstream license are included. `manifest.json` records original function lines and SHA256 hashes. New harness plumbing supplies Case A, enabled selected cooling, units=1, independent RR/DR decomposition and the temperature grid.

Offline reproduction from this directory:

    gcc -std=c99 -O0 -Wall -Wextra -Wno-unused-parameter grackle_literal_reference.c -lm -o /tmp/igm-reference
    /tmp/igm-reference > /tmp/igm-reference.csv
    cmp grackle_literal_reference.csv /tmp/igm-reference.csv

CSV: 96 temperature rows, 1..1e6 K logarithmic grid, exact/nextafter/relative neighborhoods around 5500 K, 9284 K and five exponential-cap joins. Float comparisons use 3e-13 relative tolerance with exact expected zeros. The raw reference is NOT an observational or empirical fit-accuracy validation.

Source chemistry CI floors tiny=1e-20 are retained and exposed. Original exp[-min(ln(1e30),E/T)] caps are retained. Diagnostic contribution fields report full floor-selected/cap-active channel values, not corrections to an unmodified physical fit. Grackle's historical kboltz=1.3806504e-16 is retained only inside its source cooling formula. Existing HHeModel owns EOS kB, physical c, eV and binding thresholds.

Model channel map:
- CI k1/k3/k5; thermal sink is existing binding threshold times common event count. Do not add approximate-threshold raw ciHI/ciHeI/ciHeII cooling.
- RR k2/radiative k4/k6 and kinetic cooling reHII/reHeII1/reHeIII, once each. Escape includes binding release plus kinetic cooling.
- DR is the explicit nonradiative k4 summand, not a subtractive residual. Its chemistry is off at T<=9284 K. For coherent event ownership, reHeII2 is off in the same branch; the nonzero raw source cooling is retained in excluded-residual fields. Above the branch use reHeII2 once, plus binding release in escape.
- CE ceHI*ne*nHI, ceHeI*ne^2*nHeII, ceHeII*ne*nHeII. The middle coefficient has erg cm6/s units. No chemistry event accompanies these terms.
- Freefree brem*ne*(nHII+nHeII+4*nHeIII).
- Metastable CI ciHeIS, HH, RCT, CR, metals, molecules and dust are excluded.

Density mapping verified in upstream cool1d_multi_g.F lines 442–467. This is a fixed phenomenological point model with Case A escape, C=1 and primary-only heating. No radiation transport, source history, full time integrator, interval certificate or cosmological-history result is supplied.

CMB is a separate signed reservoir: Qgas=4*sigmaT*a_rad*kB/(me*c)*ne*Tcmb^4*(Tcmb-T). CODATA 2022 constants: https://physics.nist.gov/cuu/pdf/wall_2022.pdf. a_rad is derived from exact h,kB,c; the prefactor is 1.0178101728574782e-37 cgs. Its negative is the CMB reservoir rate. It is not counted as nonnegative escape.

`IgmPhotoInput` is external point-regression input: Gamma s^-1 plus thermal power erg/s per absorber. Photo input power is common photo events times binding plus this heat. No photon population or emissivity history is inferred from these inputs.

Temperature admission is strict on the temperature actually reconstructed by the EOS. Generic `IgmGasState::from_temperature` success does not imply chemistry admission. Floating-point reconstruction of an IC requested exactly at 1 or 1e6 K can land a fraction of an ulp outside the domain; the point RHS rejects it rather than changing thermal energy or projecting the evaluation temperature. Use a representably interior IC if needed. Exact scalar endpoints are accepted by `igm_rates`. No rounding tolerance or silent extrapolation is part of this point model.
