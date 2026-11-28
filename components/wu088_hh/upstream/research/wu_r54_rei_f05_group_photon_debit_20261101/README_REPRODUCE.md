# WU R54: original REI F05 source-native 4-group DI photon conservation perturbation

**Scientific status:** source-conditional, numerically checked, NOT the original REI photon/OTS/EoR owner accepted solution. Parent WU Draft PR #193 immutable HEAD 6f2f532b46ea153795d6aebeed7b73765b6482ac. Central REI original F05 PR #352 immutable HEAD ea8d6bf94197392c69f939f03c1673ed3afe349c; accepted original tick160/131072 and tick161 NONAUTHORITATIVE preview.

Source data: 12 exact frozen files in source_inputs, every SHA256 recorded by SOURCE_CONTRACT.json and verified at runtime. Input original first 17 F05 photon forcing nodes z_mid=5.95, three nonzero groups G1/G2a/G2b and G3 exact zero. Original REI Verner HI cross section, E^-2.5 spectral shape, actual 46,080-cell H/He/T source and Savin Table1 original 47 D/H CX rates used. Source R53 all 46k-cell D atomic photo/RR/CX/EII (frozen original gamma) is the no-D-photon-feedback regression.

Run on Python 3.11+ with numpy/scipy (matplotlib optional):

    python3 r54_group_photon_perturbation.py --out results
    python3 -m unittest test_r54 -q
    python3 -O -m unittest test_r54 -q
    python3 audit_r54.py
    python3 r54_group_photon_perturbation.py --out replay
    cmp results/R54_REI_F05_DI_GROUP_CONSERVATIVE_46080.csv.gz replay/R54_REI_F05_DI_GROUP_CONSERVATIVE_46080.csv.gz
    cmp results/R54_REI_F05_DI_PHOTON_GROUPS_4.csv replay/R54_REI_F05_DI_PHOTON_GROUPS_4.csv
    cmp results/R54_GROUP_PHOTON_DEPLETION_TRAJECTORY_256.csv replay/R54_GROUP_PHOTON_DEPLETION_TRAJECTORY_256.csv
    cmp results/R54_RESULTS.json replay/R54_RESULTS.json

Outputs:
- results/R54_REI_F05_DI_GROUP_CONSERVATIVE_46080.csv.gz : 46,080 original-cell isotope group photo absorption, charge/latent/heat, source response
- results/R54_REI_F05_DI_PHOTON_GROUPS_4.csv : 4 original energy-group photon absorption, native displacement and photon reservoir depletion
- results/R54_GROUP_PHOTON_DEPLETION_TRAJECTORY_256.csv : original 4-group source reference along 64 substeps, including actual model neutral-D totals
- results/R54_RESULTS.json : exact source hashes, all source-native numerical/physics results, canonical DAG
- results/R54_ADVERSARIAL_AUDIT.json : all 46,080 original rows and independent DOP853 three-group photon deficit
- results/R54_PHYSICAL_SOURCE_WITNESS_24.csv : 24 true source nodes (if included)
- plots : optional derived source physics visualizations

Exact model: Frozen original H/He photon fields (native original GammaHI and group N/A), original group conditional weights w_g~sigmaHI_g*N_g. DI sigma = original HI sigma under **Savin approximate** equality (NOT ab-initio DI). Native H/He opacity fixed lambda0_g=A0_g/N0_g, original photon equation perturbed by DI group sink. Source group photon ledger per g exactly cumulative DI photo events = photon deficit + displaced native H/He absorption. D chemical state includes CX/EII/photo/RR; H/He donor endpoint interpolation is explicit and tick161 remains UNAPPROVED. Gross DI photoelectron heat is NOT net REI owner heating; original H/He/OTS/photon redistribution must be coupled before admission. Source original accepted 160/131072. WU 34/49, REI central 28/88, REI working33/88, Fast4/7, delta0.

Thin Git branch intentionally SOURCE-FREE except code/results/witness/identities, so restore source_inputs from exact byte-locked full source-inclusive ZIP. Never substitute F08 S0 observer spectra or PW19 BASS_HE held donor. No main merge, no production, HH_R10 OFF, REI_L4 false, auto-next false.
