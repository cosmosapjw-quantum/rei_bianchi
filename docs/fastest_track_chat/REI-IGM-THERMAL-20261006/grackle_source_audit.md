# Pinned Grackle source audit and independent C reference

Pinned commit: `af7939494ce65007887ada7b98d1813df6843346`.
Source: https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/rate_functions.c
Caller: https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/cool1d_multi_g.F#L442-L467
Constants: https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/phys_constants.h
Macros: https://github.com/grackle-project/grackle/blob/af7939494ce65007887ada7b98d1813df6843346/src/clib/grackle_macros.h
License: retained verbatim in `upstream_LICENSE`.

## Literal source reference

`grackle_literal_reference.c` contains untouched source bodies, automatically extracted by `extract_grackle_reference.py`. Only dependency plumbing, a minimal chemistry-data struct, explicit HeII RR/DR decomposition, temperature grid and CSV emission are new. Settings: Case A, all listed cooling enabled, units=1. Macro defaults are `tiny=1e-20`, `dhuge=1e30`, `tevk=1.1605e4`; source Boltzmann constant is 1.3806504e-16 erg/K. This older kboltz is intentionally retained for source parity. CMake/standard make settings and included type headers checked contain no tiny override; arbitrary custom compiler overrides are outside this audit.

Reproduce:

```
python extract_grackle_reference.py
gcc -std=c99 -O0 -Wall -Wextra -Wno-unused-parameter grackle_literal_reference.c -lm -o grackle_literal_reference
./grackle_literal_reference > grackle_literal_reference.csv
```

Result: 96 temperature rows on a 0.1-decade grid from 1 to 1e6 K, plus exact, nextafter and relative-1e-8 neighborhoods of 5500, 9284 and five exponent cap joins. Requested column order after T is k1,k3,k5,k2,k4-RR,k6,k4-DR,ceHI,ceHeI,ceHeII,reHII,reHeII1,reHeIII,reHeII2,brem. Extras are source k4 total and branch-matched DR cooling.

CSV SHA256: `50ece50b98792c6c0210d6b11e2aec29b4caa4acd96ff9e09a31274dcdff4565`.
Source blob SHA1: `e8e8a38148c8a6c8029eab6663c718b38b30b8ff`.
Function lines and body hashes: `grackle_reference_manifest.json`.

All CSV entries checked finite/nonnegative, RR+DR checked against literal total, and matched DR branches checked across all 96 rows. These checks characterize the independent reference; they do not validate the new provider until compared externally.

## Source semantics and coherent mapping

Chemistry event coefficients have cm^3/s units:
- k1: HI collisional ionization; k3: HeI collisional ionization; k5: HeII collisional ionization.
- k2: HII radiative recombination; k6: HeIII radiative recombination.
- k4: HeII radiative plus dielectronic recombination. The radiative term is 3.92e-13/(T/11605)^0.6353. Compute DR directly from its source expression, never by subtracting RR from total because cancellation hides tiny DR events.

Cooling density mapping from the actual caller:
- ceHI × ne × nHI.
- ceHeI × ne^2 × nHeII. This is metastable-HeI cooling, with coefficient erg cm^6/s. It is NOT ordinary ground-state ceHeI × ne × nHeI.
- ceHeII × ne × nHeII.
- reHII × ne × nHII; reHeII1 × ne × nHeII; reHeII2 × ne × nHeII; reHeIII × ne × nHeIII.
- brem × ne × (nHII+nHeII+4 nHeIII).

Except metastable ceHeI, listed cooling coefficients are erg cm^3/s. reHeII1 is RR kinetic-energy cooling; reHeII2 is DR kinetic-energy cooling (Cen 1992 in source). They are not interchangeable and neither should be divided by total k4 when constructing separate RR/DR event yields.

For an ionization-potential ledger, use a positive ionization reservoir Eion. CI changes Eion by +I R and thermal energy by -I R. RR and DR change Eion by -I R and thermal energy by -Lambda, while emitted photon power is +(I R+Lambda). This retains both binding and kinetic contributions once each. Dividing the literal reHeII2 by its nonzero DR event rate gives approximately 40.05–40.20 eV/event over 1e4..1e6 K; that is kinetic cooling, before adding HeI binding energy to total photon emission. This ratio is a diagnostic of separate approximate fits, not an additional fitted constant.

## Branch and floor caveats

- At T/11605<=0.8 (T<=9284 K), k4 DR is exactly absent; reHeII2 has no such branch. Its capped exponent leaves a positive raw cooling tail even at 1 K (1.24e-43 erg cm^3/s).
- Adopted coupled-ledger policy: set DR event rate AND DR cooling to zero on this low-temperature branch; retain raw reHeII2 as excluded-residual diagnostic. This is an explicit coherent adaptation, not literal parity for raw cooling below 9284 K. Do not divide low-branch raw reHeII2 by zero DR rate.
- Literal k1 is floored to tiny below the same temperature; k3 and k5 equal tiny throughout that lower branch. These are numerical source floors, not a claim of accurate physical low-temperature ionization. Maintaining source parity means exposing this caveat rather than silently treating them as closed channels.
- k2 has a separate 5500 K branch, with <=5500 using k4. No smoothing was applied.
- Capped excitation exponent join temperatures (K): ceHI 1713.2627781428682; ceHeI 190.78556590009853; ceHeII 6856.61232732308. DR cooling exponent joins: main 6803.946883150946; auxiliary 1360.789376630189. The latter DR joins are below its coherent matched-channel active branch.

## CMB coefficient from fundamental constants

For nonrelativistic Maxwellian electrons Thomson-scattering an isotropic blackbody, net gas thermal power is

Qgas = 4 sigma_T a_rad kB/(me c) × ne × Tcmb^4 × (Tcmb - Tgas).

It is positive heating below Tcmb, negative cooling above, and exactly zero at equality. No chemical energy or ionization event accompanies this process. This expression follows from the mean Thomson energy transfer, with the radiation energy density a_rad Tcmb^4; a_rad=4 sigma_SB/c.

NIST CODATA 2022 source: https://physics.nist.gov/cuu/pdf/wall_2022.pdf (NIST SP 961, May 2024, verified 2026-10-06). CGS conversion:
- sigma_T = 6.6524587051e-25 cm^2
- me = 9.1093837139e-28 g
- kB = 1.380649e-16 erg/K (exact)
- c = 2.99792458e10 cm/s (exact)
- h = 6.62607015e-27 erg s (exact)
- sigma_SB = 2 pi^5 kB^4/(15 h^3 c^2) = 5.6703744191844286e-5 erg cm^-2 s^-1 K^-4
- a_rad = 7.565733250280004e-15 erg cm^-3 K^-4
- 4 sigma_T a_rad kB/(me c) = 1.0178101728574782e-37 erg s^-1 K^-5.

At a chosen Tcmb0=2.7255 K this becomes 5.6163159675264852e-36 × ne × (1+z)^4 × (Tcmb-Tgas) erg cm^-3 s^-1. The value 2.7255 K is an explicitly chosen CMB normalization, not a CODATA constant.

Grackle comp_rate returns 5.65e-36, and its caller uses Tcmb=2.73(1+z). Fundamental expression with 2.73 K gives 5.6534997256374913e-36, consistent within 0.062% rounding. Prefer the explicit physical formula so radiation normalization and sign are unambiguous.

## Gaps and deviations

NIST constants are directly verified. Attempts to retrieve a full external IGM/Compton formula reference via Galacticus docs, arXiv PDF, and a CiteSeer paper mirror failed; the CMB formula above is an explicit physical derivation, not claimed as verified quotation from those pages. Search snippets were not used to establish implementation behavior. The fixed-version code and its direct caller are authoritative for the source channel mappings. Independent provider comparison remains the parent's verification step.
