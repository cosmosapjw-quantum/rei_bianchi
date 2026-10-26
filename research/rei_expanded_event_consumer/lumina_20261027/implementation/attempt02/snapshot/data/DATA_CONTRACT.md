# Lumina public numeric-data intake

Status: four exact public source files acquired; schema inspected. Retrieval date: 2026-10-26 UTC. This lane performed downloads and bounded text/schema checks only; no scientific IVP, interpolation, fit, digitization, or new integration.

Discovery: <https://lumina-simulation.com/data-access/>. The four links were followed from the official table, not guessed. `fetch_attempts.json` records each exact URL, HTTP 200, response headers, byte count and SHA-256. Source `.txt` files are unmodified. `schema_audit.json` gives row counts, coordinate ranges, endpoint rows and order checks. `data_access_source.html` is the exact documentation-page response (110959 bytes; SHA-256 fbd940146029ed2d6e34ceba6b79fd749b332c4a8f419477990113cf13ca10d2).

| File | Rows × columns | Coordinate coverage | Value semantics | Paper figure |
|---|---:|---|---|---:|
| sfrd_lumina.txt | 246 × 2 | z 27.433528 → 2.991495 | cosmic SFR density, solar masses yr^-1 cMpc^-3 | 9 |
| HI_reion_lumina.txt | 258 × 8 | z 29.428494 → 4.774995 | median and dispersion of sub-box volume-weighted neutral-H fraction | 17 |
| HeIII_reion_lumina.txt | 294 × 8 | z 29.428494 → 2.992408 | median doubly-ionized-He fraction; dispersion labels require resolution | 22 |
| tau_cmb_vs_z_lumina.txt | 981 × 2 | z 0 → 49 | cumulative Thomson optical depth, dimensionless | 26 |

All four are simulation predictions, not observed samples. Decimal columns parse as finite floating-point values. Each coordinate sequence is strictly ordered. The files have no observational covariance, measurement errors or likelihood.

## Important statistic and schema distinctions

HI/HeIII rows summarize 125 sub-volumes of side 100 comoving Mpc. Their median is not a mass-weighted global ion fraction. Spatial quantile bands are not observational confidence intervals. The 500 cMpc box and 100 cMpc sub-box units are comoving; no h^-1 factor is present in those quoted sizes.

The common header declares columns `z, median, p15.87, p84.13, p2.275, p97.725, minimum, maximum`. Every HI row respects that ordering. In HeIII, 203 of 294 rows violate that declared ordering; all 294 respect the reverse ordering of the six dispersion columns. At z=2.992408 the raw columns named minimum and maximum are respectively 0.995683316 and 0.954207656. Preserve the raw header and bytes. Admit the median independently; leave named HeIII quantiles unresolved.

Paper Figure 22 plots x_HeI+x_HeII, whereas the downloadable file is named and headed x_HeIII. Under the paper's three-charge-state helium normalization, x_HeIII=1-(x_HeI+x_HeII). Complementation reverses percentiles: Q_p(1-X)=1-Q_(1-p)(X). This explains a candidate origin of the header discrepancy but does not independently establish the export procedure. A later adapter must state the mapping it adopts and retain this discrepancy, or obtain an author clarification. Do not relabel the raw source silently.

The tau table ends at 0.0543742529 for z=49. The paper computes it from proper electron density using mass-weighted ion fractions, and assumes full HII/HeIII below z=3 with Y_p=0.24. A fresh tau comparison cannot substitute the downloadable volume-weighted medians into that integral. It needs mass-weighted HII, HeII and HeIII histories and the same low-z completion/cosmology.

## Scope of the next benchmarks

1. HI benchmark: forward model the same sub-box volume-weighted statistic on common z support; compare the median and separately the spatial spread. The table ends at z=4.774995, so lower-z HI must not be silently extrapolated.
2. Helium benchmark: compare the HeIII median, or its explicitly transformed complement, while preserving HeI+HeII versus HeII distinctions. Treat named HeIII intervals as unresolved until the mapping is explicit.
3. Integrated tau benchmark: use the published cumulative tau curve directly as a model prediction and separately a chosen observational CMB likelihood. Any independent reconstruction must supply mass-weighted species histories.
4. T0 and Gamma benchmarks: no numerical Lumina T0, Gamma_HI or Gamma_HeII download is linked in the official Global Statistics table on this retrieval. They remain input dependencies, not zero arrays. Paper Figure 24 defines T0 through a temperature-density fit with 0.3<Delta<10; Figure 18 selects x_HII>0.5 and n_H<0.106 cm^-3 for Gamma_HI; Figure 23 uses the same density cut without ion-state masking for Gamma_HeII. Like-for-like comparison needs those selections and fit definitions.

The physically relevant three axes are (i) coordinate and gauge conventions, including z versus scale factor and proper versus comoving densities; (ii) species normalization, charge/electron accounting and averaging invariants; (iii) estimator-matched observables. Additional species in the parent project, including free neutrons and tritium, remain independently specified state variables: these H/He tables neither measure them nor authorize setting them to zero. A generalized electron or baryon sum must include their actual charges/masses and initial conditions. Lumina's three helium charge states do not by themselves resolve helium isotopes.

## Access and provenance boundaries

The official site makes these four small tables public while bulk simulation access is by request. The article's data-availability section states a planned public release in 2028. No request to the authors was sent. No bulk snapshot or grid was downloaded. The documentation notes uint32 particle coordinates and nonconstant full-physics dark-matter masses, so a future field adapter must read file metadata rather than assume ordinary float positions or a constant particle mass. The paper gives the integer-position conversion factor L_box/2^32; units and cosmological scaling still belong to the dataset metadata. Cartesian and light-cone products change radiation field content at z=4.75.

Primary interpretive source: <https://arxiv.org/html/2605.15310v2>, Figures 17, 18, 22–26; Sections 8.1–8.4 and 9.1; Data Availability. Official project parameters: <https://lumina-simulation.com/project-description/>. Exact original user article URL: <https://academic.oup.com/mnras/article/552/4/stag1469/8971942> (search-service direct open returned inaccessible in this lane; no claim of publisher-byte download).

Failure handling: the first raw homepage urllib request returned HTTP 403; subsequent distinct linked numeric-file requests with a standard user-agent succeeded. A local optional BeautifulSoup import was unavailable, so standard-library HTML parsing was used for a limited documentation-text inspection. Neither event affected acquired numeric bytes. No repeated failing URL loop occurred.
