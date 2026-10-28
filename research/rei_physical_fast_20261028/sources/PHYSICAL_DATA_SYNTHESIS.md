# Concrete physical data for the next fast-route source adapter

2026-10-28. Selected user skill actually read: `skill://user/6aa0657100b08191b7d67482d1f97c1d/physmath-research-loop`, built-in protocol 1.0.0, SKILL plus RESEARCH_POLICY, THEORY_LOOP and EVIDENCE_AND_HANDOFF. Read prior fast STATE/F4 obligations, IC/bath proposal and phenomenological source synthesis. Preserve PR249 HEAD `c23836847261851757caef50913be1c08379d4f0`. This lane retrieves and maps data; it runs no rates campaign, solver, plot or scientific test. Historical physical fast progress remains 4/7; the completed phenomenological 7/7 and default ON_refined history have a different scope.

## Ready inputs, rather than a bibliography

| File | Actual input | Support and use |
|---|---|---|
| `BECKER_BOLTON_2013.json` | Seven measured/inferred log10 Gamma_HI values and full 7x7 statistical covariance; published thermal-slope and Jeans systematic shifts | z=2.4–4.75; immediately usable conditional correlated likelihood |
| `GAIKWAD_2023_GAMMAHI.json` | Twelve Gamma_HI central values with asymmetric total marginalized uncertainties | z bins 4.9–6.0, half-width0.05; comparison data, joint covariance not recovered |
| `PUCHWEIN_2019_FIDUCIAL.json` | All 59 primary fiducial UVB rows: HI/HeI/HeII photoionization and photoheating | z=0–15.1; physical-model forcing table, not observations or a spectrum |
| `lumina/sfrd_lumina.txt` | 246 rows of simulation cosmic star-formation-rate density | z=27.433528→2.991495; Msun/yr/cMpc^3 |
| `lumina/HI_reion_lumina.txt` | 258 rows, median and subbox scatter of volume-weighted HI fraction | z=29.428494→4.774995; simulation comparison |
| `lumina/HeIII_reion_lumina.txt` | 294 rows of HeIII fraction columns | z=29.428494→2.992408; raw percentile labels need the correction below |
| `lumina/tau_cmb_vs_z_lumina.txt` | 981 rows of cumulative model Thomson depth | z=0→49; endpoint0.0543742529; model assumptions below |

All numerical files contain factual tables only. Retrieved text preserves numeric content; exact downloaded-byte identity is not claimed. Original tables/headers remain identifiable. `LUMINA_DATA_PROVENANCE.json` binds the four actual advertised URLs, row counts and endpoints.

## Directly executable observational mapping

[Becker & Bolton 2013](https://academic.oup.com/mnras/article/436/2/1023/1118137), section4.2 Tables1–2, gives d=log10[Gamma_HI/(1e-12 s^-1)] at z=(2.4,2.8,3.2,3.6,4.0,4.4,4.75): d=(0.015,-0.066,-0.103,-0.097,-0.072,-0.019,-0.029). Table2 prints 100C; the machine file divides by100 and symmetrizes the upper triangle. It is a covariance in dex^2, not fractional or linear-rate covariance. The primary fiducial temperature-density slope is gamma_TDR=1.4. Published changes to1.2/1.6 supply signed nuisance directions; Jeans-smoothing shifts are separate. Their total systematic errors must not be added again to C as if independent Gaussian errors.

For predicted m_i=log10[Gamma_model(z_i)/(1e-12 s^-1)] and explicit systematic displacement delta_i(theta), the conditional statistical likelihood is

    -2 log L = (m-d-delta)^T C^-1(m-d-delta) + log det C + 7 log(2pi).

The thermal-slope interpolation delta_gamma=((gamma_TDR-1.4)/0.2)r uses the tabulated endpoint vector r only within1.2≤gamma_TDR≤1.6; that interpolation and any nuisance prior are adapter choices. These observations are inferred through hydrodynamical/thermal modeling. Their FLRW calibration cannot be applied as an exact likelihood for a large-shear Bianchi universe without an observable-model comparison. A source-amplitude fit using them can be admitted conditionally under the stated calibration cosmology.

[Gaikwad et al.2023](https://academic.oup.com/mnras/article/525/3/4093/7259921), Table3, supplies a newer high-redshift interval. Rates decrease from0.501(-0.232,+0.275) to0.145(-0.087,+0.157), in1e-12 s^-1, betweenz4.9 and6.0. Their uncertainty includes thermal/model/cosmic-variance/observation effects and marginalizes other inferred quantities. No joint redshift covariance was recovered. A split-normal independent-bin score would be an explicit approximation; it is not the published joint likelihood. Gamma, mean free path, neutral fraction and emissivity in that table are jointly derived and must not be multiplied as independent constraints. Thus the implemented first likelihood should use the complete Becker–Bolton covariance, with the high-z table kept as a separate comparison or declared approximate extension.

## Actual physical rate provider and its boundary

[Puchwein et al.2019 primary ancillary table](https://arxiv.org/src/1801.04931v1/anc/rates_fiducial.txt) and [readme](https://arxiv.org/src/1801.04931v1/anc/readme.txt) were actually retrieved, resolving the old located-but-not-downloaded gap. Alternating columns are Gamma [s^-1] and heat [eV/s per target atom/ion] for HI, HeI, HeII. Use r_photo/Href=y_target Gamma and heat/Href=y_target heat_rate. This is the fiducial non-equilibrium prescription. Equivalent-equilibrium rates and the TREECOOL format are different products; TREECOOL heating uses erg/s. The last raw Compton column is retained but excluded from the adapter until its precise normalization is bound.

The provider ends atz15.1, whereas the saved trajectory begins at20. Reject out-of-domain requests or explicitly add a physically justified prehistory. Do not extrapolate by endpoint clamping and call it a source prediction. Rate moments do not uniquely determine a spectrum: six moments cannot supply Li photoionization or MeV photodisintegration integrals. A common multiplicative amplitude is a declared UVB shape assumption, not evidence that all six rates have measured common uncertainty.

## User's Lumina paper: actual contents and newly recovered public data

The exact [MNRAS stag1469 article](https://academic.oup.com/mnras/article/552/4/stag1469/8971942) is Zier et al., *Introducing the lumina project: large-volume radiation-hydrodynamic simulations of the epochs of hydrogen and helium reionization*, published26October2026. It is a simulation paper, not a direct observed17-isotope source table. The full release is stated for2028, while figure data are already advertised. Following the actual homepage Data link to [data-access](https://lumina-simulation.com/data-access/) revealed the four numerical files above. This supersedes the prior guessed `/data` route failure and prior statement that no numerical Lumina table was retrieved. No author contact or private-data request occurred.

Figures17/22 use125 subboxes of side100cMpc and percentile scatter of their volume-averaged fractions. Those intervals describe simulated spatial variation, not measurement errors. The public HeIII file preserves a labeling inconsistency: at its final row the column named15.87 percentile is0.994614769, above the median0.993331657, while the84.13 column is0.990400757; the named min exceeds the named max. Figure22 plots the complementary quantity x_HeI+x_HeII. These values are consistent with complementing columns without relabeling percentiles. Preserve raw data and record the interpretation; for a complemented random variable the correct rule is Q_(1-X)(p)=1-Q_X(1-p), with min/max exchanged. The table's percentile labels are not silently trusted or sorted. The median may be compared as xHeIII under its file convention. Figure26 computes tau using simulated electrons abovez3 and assumes fully ionized H and He belowz3, explaining why its tabulated range exceeds the simulation's final redshift.

The recovered SFRD is a real simulation-based stellar-history input. To turn it into emissivity, one still needs the age/metallicity spectral-yield convolution and escape fraction, followed by transport to a local radiation field. Per-comoving-volume source becomes proper emissivity with one factor(1+z)^3; per-Href conversion divides by actual nHref. A global SFRD does not supply local n/T injection, projectile energy spectra, nuclear yield kernels or charge-state branches. Global volume-weighted ion fractions also differ from a homogeneous parcel's number fraction when density correlates with ionization.

## Remaining physical F4 obligations and next action

Adopt the correlated Gamma_HI likelihood plus the fiducial physical UVB-rate provider as a narrowly identified F4 photon-source subtask. This supplies actual data, covariance, normalization and finite-domain behavior now. Keep ON_refined as the saved phenomenological display default; do not relabel its arbitrary 20eV/100eV/MeV photon bins, CR flux, direct isotope injections or escape/slowing hazards as calibrated by Gamma_HI. UV-only constraints do not close physical neutron/tritium production, MeV spectra, cosmic-ray yields or transport.

The proposed8K IC profile remains incompatible with unchanged300K donor temperature/electron/photon hazards. A future physical trajectory must choose a coherent initial bath and prehistory, with its own thermal evolution and isotope coverage. Atomic/UV data alone leave lithium and nuclear source closure open. The old large-shear donor is a stress-test background, so transferring inferred observational errors to it also needs a declared conditional interpretation.

The real deliverable is an observation-backed source adapter/likelihood contract and recovered simulation-source history. Source calibration, a new physical trajectory and an all-particle physical prediction remain distinct next computations. This lane ran no such computation and measured no scientific CPU debit; it does not silently assign zero cost or reset historical spending.

## Tool/query provenance

Actual selected SciSpace search: “Which public primary data tables provide redshift-dependent hydrogen and helium photoionization and photoheating rates from the Puchwein Haardt Haehnelt Madau2019 ultraviolet background, and what are the differences between fiducial non-equilibrium and equivalent equilibrium rates?” SUCCESS; primary Puchwein paper identified. Actual Exa search/fetch: exact userLumina URL, project homepage, arXiv1801.04931; Becker–Bolton Table1/2 query and full-text fetch; Gaikwad2023 primary full text; exact ancillary rate/readme URLs; all four advertised Lumina numeric URLs. All succeeded. Web-tool link inspection corroborated the primary rate table and exposed the actual Lumina Data links. A www-prefixed homepage open failed in that tool while Exa and the canonical non-www page succeeded; this did not establish absent data.

A current-literature search with recency730days additionally located Gaikwad2025 HeII arXiv2503.04893 and a2025 z~2.4 HETDEX UVB measurement arXiv2504.13253. Their numerical products were not adopted in this bounded lane. Accordingly these inputs are concrete historical/current primary sources, not a claim to a complete latest global posterior. No full article bodies are saved in the deliverable.
