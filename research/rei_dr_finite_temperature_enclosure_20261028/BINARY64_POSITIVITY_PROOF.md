# Binary64 positivity margins — explicit source proof

This is a written proof supplement to D2 in THEORY_AND_CONTRACT.md, not a numerical execution. It closes the source-specific coefficient inequalities without waiting for the pending exact-rational runtime diagnostic. No source value, closure or runtime domain changes.

Let u=2^(-53)<10^(-15). The selected normal binary64 coefficient images satisfy c_hat=c_decimal(1+delta), |delta|<=u, under the stipulated round-to-nearest conversion. All nine resonance energies are integers below2^53 and therefore represented exactly. The positive represented s and k do not change signs.

For a positive source amplitude a and magnitude b of the negative amplitude, a_hat-b_hat >= (a-b)-u(a+b). For energy weights, a_hat E0-b_hat E2 >= (a E0-b E2)-u(a E0+b E2). The following are exact arithmetic on the ORIGINAL DECIMAL LEXEMES, explicitly not new computed binary64 values:

| Row | a-b | a+b | a E0-b E2 | a E0+b E2 |
|---|---:|---:|---:|---:|
| He+2:1 |0.00139515|0.00143885|637.078005|675.914195|
| Li+3:1 |0.0000286347|0.0000301853|18.01939437|19.30189563|

For example He+ a E0=656.4961, b E2=19.418095; Li+ a E0=18.660645, b E2=0.64125063. Each positive difference exceeds10^(-15) times its corresponding sum by many orders of magnitude. Therefore both represented-image margins are strictly positive. Also E2>E0 exactly (888700>463300 and827100>634500); both middle coefficients remain positive under binary64 conversion. D2's rewritten lower bounds are thus valid for these exact represented rows.

The Li2+ row has three positive normal coefficients and positive exact energies, so both sums are strictly positive for every T>0. The admitted physical/model-use domain remains100..1e6K. These are properties of the source functions, not atomic fit-accuracy or callback-rounding claims.

The pending worker's Fraction margins will be a serialization/provenance control of this independently proved inequality. No test count is substituted for the proof.

