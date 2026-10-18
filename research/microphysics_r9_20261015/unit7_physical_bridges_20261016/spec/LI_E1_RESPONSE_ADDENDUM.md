# Unit7 A2: complete the discrete E1 plus two-photon source response

Frozen 2026-10-16. This is a separate constructive follow-on to A1; the original A1 contract and results are immutable. Requested authority Astra; observed model UNKNOWN. Reuse A1's established provider cross-section function and shell semantics, then add the actual saved E1 line measure. No A1 integration or convergence ladder is rerun.

## Actual input and support

The immutable Unit6 `results/laneB/twophoton_E1_lines.csv` contains 6608 transition rows for the same 32 mixtures. Each row already carries the mixture-weighted `photon_count` N_i and `photon_eV` E_i. Do not multiply again by a statistical-shell weight or by the terminal 2s probability. Rows with equal E_i but different transition identity are separate contributions to be summed; do not drop them as duplicates.

The actual maximum E1 photon energy is 121.60088228541453 eV, larger than the two-photon endpoint 91.83842857919419 eV. A2 expressly extends application of the unchanged provider prescription through this actual maximum. This lies within the existing source's high-energy HDS domain; there is no new fit, interpolation, shell, or source assumption. Per mixture let Ecap=max(max_i E_i,Delta). Never clip E1 photons at Delta.

The source per injected precursor is the measure

    dN(E)=sum_i N_i delta(E-E_i)dE + S_cont(E)dE,

with exactly the A1 conditional illumination convention F=J*dN, J=1 precursor-equivalent m^-2 s^-1. The continuum component is the asymptotic delayed emission already computed in A1; E1 is the completed cascade line yield. Their sum represents the completed source, not a new chronological source history or instantaneous rate after original injection.

## Finite sums and component combination

For shell a, threshold B_a (2s=5.392 eV, 1s=64.39 eV), and band b, evaluate the existing provider partial sigma_a(E_i) in m^2 and form

    G_E1,a,b = sum_{i in b} N_i sigma_a(E_i),
    W_E1,a,b = eV_J sum_{i in b} N_i sigma_a(E_i) E_i,
    K_E1,a,b = eV_J sum_{i in b, sigma_a>0} N_i sigma_a(E_i)(E_i-B_a),
    Q_E1,a,b = eV_J B_a G_E1,a,b,
    X_E1,1s,b = eV_J (64.39-5.392) G_E1,1s,b,
    X_E1,2s,b = 0.

The masked K sum avoids interpreting a below-threshold negative energy multiplied by zero. At the exact K edge use A1's PH1 branch for both occupied shells. Sum 1s and 2s for shell=total. For every response field, combined=E1+continuum, where the continuum values are read from A1 `li_photo_response.csv`, selecting exactly `quadrature_nodes=256` and `authoritative=True` (parse the CSV Boolean explicitly). Never sum the64/128/256 rows together. Preserve imported continuum numbers rather than recalculating or reformatting them through a new solver.

Keep the five A1 band names with these canonical sets, intersected with each component's actual support:

| Band | Set |
|---|---|
| sub_Lyman | 5.392 <= E < 13.6 |
| upper_old | 13.6 <= E < 64.39 |
| extension | 64.39 <= E <= Ecap |
| covered_total | 5.392 <= E < 64.39 |
| full_total | 5.392 <= E <= Ecap |

Only the first three are disjoint; covered_total=sub_Lyman+upper_old and full_total=covered_total+extension. Do not sum all five as if disjoint. Existing continuum bounds were clipped at Delta; their named-band values remain exactly valid after the Ecap extension because the continuum is zero above Delta. Export component support bounds or explicit source_cap_eV so that different E1/continuum endpoints remain visible. No actual saved line falls exactly at5.392,13.6,64.39 eV, but the interval convention is still frozen.

Save one response table with 32 mixtures x5 bands x3 shells x3 components (`E1`,`continuum`,`combined`), exactly1440 rows. Use A1's five response field names. Derive mean absorbed energy W/(eV_J*G) when G>0 and null otherwise. Export per-mixture full_total shell=total continuum fractions and E1 fractions of G,W,K, plus1s contribution fractions, with null denominators handled explicitly. These distinguish which part of the completed source drives Li I absorption.

Save a source-moment table for all32mixtures with E1 line photon count, E1 line energy, continuum photon count/energy read from the256-node authoritative `full_source` rows in A1 `li_photo_source_moments.csv`, combined moments, saved initial_excitation_eV and closure residuals. Include low-energy E1 photons below5.392 in these source totals even though their opacity response is zero. Do not equate source total energy with cross-section-weighted absorbed energy.

## Essential checks and finite stopping rule

1. Input hashes and the32 `(species,n)` keys agree; line count6608 and maximum energy match. Every line has nonnegative finite N_i and positive finite E_i; stored `energy_eV` equals N_i*E_i. Sum all line yields per mixture and compare with the saved mixture E1_photon_count and E1_energy_eV. Do not rebuild the E1 cascade.
2. The imported continuum table has exactly one authoritative256-node row per mixture/band/shell. Combined response equals the two components; each component obeys shell addition, disjoint-band addition, W=K+Q, and Q=eV_J*5.392*G+X. Require nonnegative finite coefficients and correct zero inner-shell response for source support below64.39.
3. Full source N=sum_i N_i+N_cont agrees with E1_photon_count+2P. Full source U=sum_i N_i E_i+U_cont agrees with saved initial_excitation_eV. For source checks use1e-8 relative with1e-14 absolute floor, reflecting imported numerical continuum moments; pure line and response algebra checks use1e-11 relative with floors1e-14 photons/eV,1e-35 m^2,1e-53 J m^2. Do not require byte-equal numerical outputs.
4. Check the genuinely new energy range once: independently evaluate decimal/log-form PH1 partials at the largest actual line energy and compare with the reused kernel to1e-11 relative, floor1e-30 Mb. Retain actual values. This extends the point check to the newly used range without rerunning A1's tests or quadrature. No Fortran compiler installation is needed.

Use the existing A1 implementation by import, without changing it. Compact Python finite sums (`math.fsum` encouraged) and one targeted test file are sufficient. Numerical execution and focused checks combined must finish within5seconds extra, one thread. No continuum integration, no new convergence ladder, no rerun of A1. On failure stop with the concrete residual and return to authority; one bounded repair only if authorized. The A2 admission inherits A1's review status and never upgrades an unadmitted A1 result by addition.

The output remains a smooth direct-photoionization response under hypothetical incident normalization. K is primary photoelectron kinetic energy; Q and X are threshold/configuration bookkeeping. No temperature, actual deposited heat, Auger/fluorescence yield, final charge-state branching, transport, physical H(t), or external NCP result is inferred.
