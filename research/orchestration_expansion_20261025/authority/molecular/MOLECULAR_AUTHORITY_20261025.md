# Molecular source and data reuse authority

Scope: scientific literature and reusable input contracts, accessed 2026-10-25. No repository implementation, remote mutation, full network solve, or heavy computation was performed. The authoritative target inventory is the root auditor's inspected `rec_bianchi` PR119 `atomic_network.py`, commit `ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7`: n; H1/D/T charge 0–1; He3/He4 charge 0–2; Li6/Li7 charge 0–3, with electrons via neutrality. This is 21 nuclear/atomic states. Molecular states below are explicit expansion candidates, not existing admitted coverage.

## Exact attached paper and reading bounds

A. G. G. M. Tielens, **The molecular universe**, *Reviews of Modern Physics* **85**, 1021–1081 (12 July 2013), DOI [10.1103/RevModPhys.85.1021](https://doi.org/10.1103/RevModPhys.85.1021). The selected [Drive file](https://drive.google.com/file/d/1_0Y7D04X6jRZve_BkH-BFtViT_tMGh9o/view) is named `The molecular universe (2013).pdf`, 6,723,853 bytes, created/modified 2026-10-25. The title page, DOI, contents, sections IV.J and VIII.B.2 and targeted isotope/database/transfer contexts were actually read. Hydrated complete extracted text (358,483 characters, with extraction artifacts) is preserved locally; no claim is made that every page or cited reference was independently reviewed. Exa and SciSpace retrieved other same-title works, notably Tielens2011 and Fraser et al.2002; Drive title-page metadata resolves the ambiguity.

The paper directly points to UDfA, OSU and KIDA for reaction networks (IV.J, pp1044–45), and CDMS, JPL, Splatalogue, BASECOL, LAMDA and VAMDC for spectroscopy, excitation and exchange (VIII.B.2, pp1071–72). Its transfer-code label says RATRAN while the literal URL ends `radex.html`; the current linked primary page describes RADEX. Treat these as separate code identities.

The paper's gas-phase, surface and PAH discussion supplies a process taxonomy and motivates uncertainty propagation. It is not a complete nuclear reaction library, a source for every charge state of the target isotopes, or a ready-made cosmological closure. Grain chemistry becomes a separate model component only with a specified grain population, surface temperature, adsorption/desorption law and radiation environment.

## Verified source contracts

`data_reuse_registry.json` gives every source, units, formats, bounds, release and unresolved licence/uncertainty fields. A licence marked unresolved means its redistribution terms were not established by the pages read; public accessibility or a paper's CC licence is not substituted for a data/code licence.

| Source and relation | Concrete reusable object | Restriction affecting first use |
|---|---|---|
| LAMDA, paper-cited | HD ASCII file, version7 June2021, CDMSv2 Dec2011, Flower1999 collision source | 9 rotational levels J0–8, 8 lines, p-/o-H2 rates at50/100/200K; no HD formation/destruction data |
| CDMS, paper-cited | HD003501 and HeH+005502 catalog entries; isotope/state-specific spectral records | Live entry revisions differ from pinned LAMDA spectroscopy; starred intensity tags can mean S mu² rather than300K intensity |
| JPL, paper-cited | 6LiH(7001,v2,51lines),7LiH(8001,v2,53),6LiD(8002,v1,80),7LiD(9001,v1,90); H,D hyperfine and HD entries | Fixed-width80-character records; frequency/error MHz, E_lower cm^-1, log-intensity nm² MHz at300K; isotope abundance correction is not already applied |
| UMIST/UDfA, paper-cited | Rate22 final reaction and species files; release paper2024, DOI10.1051/0004-6361/202346908 | Full737-species network is broader than requested elements; extract exact supported subnetwork and preserve per-reaction temperature fits |
| KIDA, paper-cited | `kida.uva.2024.zip`; separate deuteration/spin network | Live maintenance observed; Exa recovered cached primary docs. 2021 advisory identifies errors in older H3+–H2 spin rates and points to Sipilä2017/Hily-Blant2018 corrections |
| BASECOL, paper-cited | State-to-state excitation rates; BASECOL2023 DOI10.1051/0004-6361/202348233 | q cm³/s,T K,E cm^-1; general1–3000K range is not a substitute for selected dataset bounds |
| Splatalogue/VAMDC, paper-cited | Discovery and exchange; SPECTCOL can match state descriptions | Underlying CDMS/JPL/BASECOL provenance remains mandatory; no independent rate authority |
| RADEX, paper-linked | Standalone non-LTE escape-probability comparison | Homogeneous isothermal1D assumption and no large-scale velocity field; endpoint collision rates are held constant outside file bounds |
| Leiden photodissociation, new recommendation | H,H−,H2,H2+,H3+,Li,LiH cross-section families; `.pd/.pi/.txt/.h5` | nm and cm²; old formats often truncate below91.2nm; isotope identity and branching must be explicit. Broad-band uncertainty categories A+20%,A30%,B×2,C×10 |
| ExoMol ADJSAAM, new post2013 recommendation | 4HeH+,4HeD+,3HeH+ direct pages;3HeD+ index; states/transitions/partition functions from Amaral etal2019 ApJ87895 | Pin `.def` fields, state completeness, file hashes and licence before ingestion. Natural-abundance cooling tables are unsuitable for a freely evolving isotope mixture |

Primary URLs: [LAMDA format](https://home.strw.leidenuniv.nl/~moldata/molformat.html), [HD](https://home.strw.leidenuniv.nl/~moldata/HD.html), [HD bytes](https://home.strw.leidenuniv.nl/~moldata/datafiles/hd.dat), [CDMS](https://cdms.astro.uni-koeln.de/classic/entries/), [JPL format](https://spec.jpl.nasa.gov/ftp/pub/catalog/doc/catintro.pdf), [JPL directory](https://spec.jpl.nasa.gov/ftp/pub/catalog/catdir.html), [UMIST downloads](https://umistdatabase.uk/downloads), [KIDA networks](https://kida.astrochem-tools.org/networks), [BASECOL](https://basecol.vamdc.eu/), [RADEX](https://home.strw.leidenuniv.nl/~moldata/radex.html), [Leiden cross sections](https://home.strw.leidenuniv.nl/~ewine/photo/cross_sections.html), [ExoMol4HeH+](https://www.exomol.com/data/molecules/HeH_p/4He-1H_p/ADJSAAM/).

Metadata discrepancy requiring preservation: the HD webpage says rotational coverage up to a v=1 level near3100cm^-1; the downloaded file instead labels nine successive J values0–8 and ends at3089.576092837cm^-1. The first adapter should represent exactly the J-labelled records and leave vibrational coverage unresolved. It must not invent v=1 transitions from the page summary.

## Molecular expansion and scientific ownership

| Object | Lead owner | First supported expansion and dependencies |
|---|---|---|
| Isotope identity, molecular composition, stoichiometry, formation/destruction rates | WU088_HH | WU-owned molecular stoichiometric compiler is the next root-selected bounded unit; no empirical rate claim is needed to prove isotope/charge invariants |
| Level-resolved spectra, radiative coefficients, absorption/emission and molecular statistical equilibrium | rec_bianchi | First HD adapter with WU isotope mapping; CDMS/JPL and ExoMol spectral additions follow record-level validation |
| Differential collisions, energy and momentum response | BASS_HE | State/collider-resolved kernels and matching energy transfers; thermal q(T) alone cannot reconstruct an angular kernel |
| External nonthermal photon/baryon injection and stopping | bass_cr | Reuse shared atomic/molecular provider with incident distribution and threshold/domain labels |
| Unified selected cosmological chemistry and transport integration | rei_bianchi | Consume certified producer objects; define cosmological radiation, density, expansion, dust and abundance context |
| Numerical infrastructure and observable consumers | vigilode; bass | Consume explicit units/provenance/contracts; no duplicate physical data authority assigned here |

Candidate stages: (1) H2/HD molecular state identities and HD line/collision fixture; (2) H−/H2+ intermediates and HD isotope exchange, with audited formation/destruction rates; (3) 3He/4He hydride H/D isotopologues and isotope-specific LiH/LiD spectral candidates; (4) H3+ deuterated spin family only with corrected state-specific rates. H2 has different radiative selection rules from HD; copying HD dipole transitions to H2 is invalid. T-bearing molecules, HeT+, LiT, and all molecular ionization stages retain explicit data gaps. H− is a newly required atomic anion, outside the current q0–1 H inventory, and must be added explicitly if its formation pathway is selected. Molecular isotope substitution does not authorize unverified rate scaling.

## Derived source contract

For a selected isotope composition, charge and electronic/rovibrational state i, keep number density n_i [m^-3], energy E_i [J], degeneracy g_i, collider identity a and rate q_ij^(a)(T) [m³/s]. Use a reaction stoichiometry matrix S and reaction fluxes R [m^-3s^-1]: dn/dt = S R plus separately defined transport. Each ordinary molecular reaction must satisfy C S=0 for the full isotope-count matrix C, and z^T S=0 including explicit electrons. Nuclear transmutations use their nuclear conservation contract; they do not obey per-isotope conservation. Baryon count and charge checks alone cannot detect mistaken D↔H substitutions.

For Maxwellian colliders at one temperature and matched state degeneracies, detailed balance gives q_lu=q_ul(g_u/g_l)exp[−(E_u−E_l)/(k_B T)]. A downward-rate table determines upward rates only under these assumptions. It does not determine a nonthermal differential scattering kernel. Missing state pairs are missing data, not zero-valued rates.

With frequency-normalized profile integral(phi_nu dnu)=1 and Einstein B defined against mean specific intensity J_nu, j_nu=(h nu/4pi)n_u A_ul phi_nu and alpha_nu=(h nu/4pi)(n_l B_lu−n_u B_ul)phi_nu, with g_l B_lu=g_u B_ul and A_ul/B_ul=2h nu³/c². Under Boltzmann populations these give j_nu/alpha_nu=B_nu(T), providing a closed LTE reference. Population inversion can make net alpha negative; do not impose positivity on net absorption to hide stimulated emission. Bare event rates and individual cross sections remain nonnegative.

Photodestruction rate per target is Gamma=4pi integral[J_nu sigma_nu/(h nu) dnu], in s^-1 for isotropic J_nu. Photon-number, energy and momentum sources require separate weighted integrals and a declared angular closure. Transforming wavelength tables must preserve the Jacobian and energy threshold. A spectrum-integrated rate at one interstellar field cannot replace sigma(nu) for an arbitrary cosmological/nonthermal spectrum. Dust attenuation, line self-shielding, radiative association photons and recombination photons must each have one owner to avoid double counting.

## Executed reference check and minimal adapter acceptance

Only one bounded source fixture was downloaded and scalar-checked: `lamda_hd_20261025.dat`,2289bytes,SHA256 `0c99fe168235d6d6dac3063093bbbe8b4a2ea15cca53c7e2987763c801fdaefb`. `hd_reference_check.json` records the actual result. For HD J1→0, E_gap/(hc)=89.227931611cm^-1 yields nu=2674986093991.7593Hz; catalog2674986094000Hz differs by−3.08066e−12 fractionally. E_gap/k_B=128.3790848294K. At100K, q10=2.7e−11cm³/s gives q01=2.2435809177e−11cm³/s and q10=2.7e−17m³/s. The two-level single-p-H2-collider critical-density estimate A10/q10=2015.56cm^-3 is a scoped arithmetic check, not a complete multilevel cooling prediction.

REC adapter acceptance: parse nine levels/eight lines/two colliders without losing J or isotope labels; exact source hash; energy/frequency agreement within catalog precision; preserve p-/o-H2 separation and all three T nodes; q-unit conversion; detailed-balance and LTE/Kirchhoff residuals; reject or explicitly flag T outside50–200K; no inferred vibrational or missing-collision coverage. Licence decision and original spectroscopy/collision citations accompany any redistributed fixture. No adapter implementation or RADEX run has been claimed.

## Actionable PR dependency nodes

1. **WU-MOL-ID/STOICH**: exact isotope composition + charge + state-family schema and compiler, selected by root as next unit. Inputs: existing21-state inventory and explicit molecular additions. Gate: isotope and charge invariants, unique identities, no implicit abundance/rate defaults. REC/HE/CR consume IDs.
2. **REC-HD-ADAPTER** depends on WU-MOL-ID: bounded LAMDA fixture and source metadata. Gate: the acceptance contract above; no global molecular coverage claim. No heavy computation needed.
3. **WU-MOL-RATES** depends on WU-MOL-ID: filtered UMIST/KIDA rows and independent paper-level comparison; specify H−/H2+ routes, electron convention, symmetry factors, collider and validity domains. Gate: conservation, orders/units, uncertainty provenance, corrected spin rates and inverse-process convention.
4. **REC-MOL-SPECTRA** depends on IDs/adapter: JPL Li isotope spectra and ExoMol He hydrides. Gate: state mapping, partition normalization, isotope coverage, file-version hash, no terrestrial abundance injection.
5. **HE-MOL-COLL / CR-MOL-PHOTO** depend on IDs and admitted data: differential kernel or photoprocess tables with explicit energy and angle coverage. Gate: moment closure, energy/momentum accounting, source-versus-absorption partition and no use of zero placeholders as measured physical data.
6. **REI-MOL-INTEGRATE** depends on admitted producer contracts: selected chemistry/transport environment, scale factors, physical-versus-comoving densities and radiation feedback. Gate: stiff-network invariants, thermal equilibrium limit, conservation residuals and domain flags. Larger runs require a separately frozen input/acceptance/budget unit.

Evidence state: paper identity and listed primary-doc contents literature-supported; scalar HD arithmetic numerically checked; radiative/detailed-balance relations derived under stated conventions; all repository integration and external-code verification not_run. No new no-go theorem is asserted. R1–R5/R8–R10 are complete for this literature/contract unit; R6 uses unit, inverse-relation and LTE consistency; R7 is only the bounded HD scalar check. Remaining obligations are record-level licences/uncertainties, exact reaction and state extraction, and actual adapter tests. These are dependencies for the PR nodes, not grounds to shrink the user's isotope target.
