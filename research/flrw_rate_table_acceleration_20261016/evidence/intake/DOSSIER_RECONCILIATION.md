# Dossier inventory and implementation reconciliation

The 73-page user dossier is **Reionization: Microphysics, Transport and Observation**, dated 14 October 2026, SHA256 `179b114f60c1f8923f9faffb7218a90f1189667c335922525cb6247a174e85a3`. Page citations below give **PDF page (printed page)**. The original PDF, extracted text, and rendered inspection image remain outside repository/public payloads. This intake uses the document as scientific content, not operational instructions.

## Inventory actually present

PDF **8 (3), Eq. 1.15**, visually checked against the rendered page, specifies seventeen entries: neutron; H1 q=0,1; D q=0,1; T q=0,1; He3 q=0,1,2; He4 q=0,1,2; Li7 q=0,1,2,3. The exact zero-based mapping is `data/dossier_species_registry.json`. It preserves those seventeen positions and appends Li6 q=0…3 at 17…20 under the user's explicit current isotope request. Thus the inventory union has **21 states**. Existing `isotope_state.rs` supplies the first thirteen bookkeeping primitives; the Li module supplies typed Li6/Li7 charge identities and conditional coefficients separately. A coupled twenty-one-state native solver is not established by this mapping.

The same page explicitly leaves free electrons, photons, molecules, negative ions, additional nuclei, and nonthermal populations outside that vector. It names no molecular or negative-ion species list. Beryllium can feed lithium; PDF **9 (4), Eq. 1.21** treats bound/continuum-electron and hyperfine-dependent electron capture with matched daughter counts. This equation does not assign a Be isotope number or supply a complete Be provider. Be7 and Li8/Li9 remain separately identified prior-PR ancestry dependencies rather than invented additions to Eq. 1.15.

The latest user request to reflect the dossier is fulfilled immediately by this complete inventory/convention map and dependency update. It does not silently activate T/He3/neutron/Be/molecular reaction providers. The earlier Li-only added-provider scope remains the implemented coefficient work; D/T/He3/neutron bookkeeping was already present and is now explicitly reconciled to the report.

## Conventions with immediate implementation consequences

| Dossier location | Scientific content | Consequence for current work |
|---|---|---|
| PDF 5 (iv), 6–7 (1–2), 22 (17) | Signature (-,+,+,+); proper seconds differ from length time s=ct; local coefficients in material rest frame | Keep source coefficients background independent and physical-second units; no H or expansion division |
| PDF 8–10 (3–5), Eqs. 1.14–1.24 | Abundances per baryon, isotope/charge conditional probabilities, finite-time origin, omitted reservoirs | Convert to existing proper-SI densities using an explicit nB; do not renormalize a retained subset to unity or infer charge populations from one scalar electron fraction |
| PDF 9 (4), Eqs. 1.17–1.19 | Atomic versus nuclear rest-mass convention and composition-dependent nB normalization | Free-electron rest energy and binding energies counted once; caller mass/abundance convention is not replaced by A times an arbitrary mass unit |
| PDF 7–8 (2–3), Eqs. 1.9–1.13; PDF 32–33 (27–28), Eqs. 2.60–2.66 | Translating-particle heat capacity, particle-creation term, common event number/energy balance | H/He-only EOS cannot silently become a full-isotope mixture EOS when Li or other spectators are appended |
| PDF 13 (8), 50 (45) | Total free-electron current includes retained active electrons; only thermal electrons enter the common-temperature heat capacity | Distinguish n_e,free from n_e,thermal; photon/nonthermal energy has separate owners |
| PDF 23 (18), Eqs. 2.4–2.9 | Finite-mass one-electron E1 transitions include reduced mass and an effective dipole charge | No generic isotope mass rescaling of neutral/partly stripped Li or fitted CI/RR/DR follows |
| PDF 24–25 (19–20), Eqs. 2.11–2.23 | Infinite-mass ground-state hydrogenic photo/RR number and energy moments | The Li III capture example is level-specific, not total Badnell RR, Case A/B, or a complete isotope-native Li closure |
| PDF 31–32 (26–27), Eqs. 2.55–2.64 | Radiation-integrated number/excess-energy rates; spectral hardening; kinetic versus binding energy | Γ[Jnu] and heating remain radiation functionals; rate tables alone cannot create a thermal or emitted-photon ledger |
| PDF 34–35 (29–30) | Conditional HYREC reference and scalar xe normalization | Reference xe does not determine the 21 charge populations or radiation distortion; no default cosmological IC is imported |
| PDF 47–49 (42–44) | n+p↔d+γ with explicit reciprocal ensemble assumptions | A nuclear derivation is not runtime nuclear-rate admission; preserve ensemble and daughter-energy dependencies |
| PDF 59 (54) | Proper density conversion, changing heat capacity, forced photon source | No extra a^-3 on an already proper density; cm^-3→m^-3 factor10^6 and erg cm^-3 s^-1→J m^-3 s^-1 factor0.1 |

The dossier uses a composition-specific helium/H mass ratio 3.97153 in its conditional recombination example, PDF **34 (29)**, and an explicit four-hydrogen-mass helium approximation in the separate warm-gas example, PDF **59 (54)**. These are different declared conventions; they must not be substituted into one another without conversion. Existing caller parameters remain unchanged.

## Constructive full-mixture thermal-CX dependency

Under a common nonrelativistic monatomic temperature and fixed local volume, define the volumetric heat capacity

    C_V = (3/2) k_B [sum of translating atomic/nuclear particle densities + n_e,thermal].

Photons and separately retained nonthermal electrons are excluded. Molecular internal modes require a corresponding extended closure if molecules are later included. H/D charge exchange conserves the number of nuclei and total free-electron count, so with spectators fixed its energy increment is converted using **the total mixture C_V**, not a pure H/D denominator. For that substep, ΔT=Δu_th/C_V and the same exchange event supplies Δu_th=-Δu_chemical. In a generally ionizing mixture, the temperature equation also retains -T R_th/n_th from Eq. 1.11; a constant heat-capacity shortcut would fail when particle counts change.

This directly specifies the next dependency `FULL_NETWORK_THERMAL_CX_COMPOSITION_AND_EOS_CONTRACT` identified by the collected native-CX update. That existing native H/D result is scoped to a pure fixed-volume H/D system and rejects He/Li spectators. Its two possible owners, atomic RHS or thermal substep, remain mutually exclusive per event. The new registry and Li coefficient adapter do not change those guards or activate a full-mixture energy closure.

For a complete mixture, use Eq. 2.64: local thermal power equals total matter power minus the eventwise chemical-energy change, with every radiation/nonthermal leg assigned exactly once. Li number CI/RR/DR coefficients lack the corresponding complete kinetic/emission moments. The dossier supplies useful hydrogenic moment constructions and future reference tests, while correlated neutral/partly stripped Li and source-fit mappings remain separate required inputs.

## Practical next actions and current compatibility

The current prepared H/He/D coefficient reuse and opt-in Li6/Li7 number provider are compatible with the report's local-rest-frame separation. Current coefficient interpolation accuracy remains separate from model/fit uncertainty, as the dossier states in PDF **5 (iv), 35 (30)**. Its hydrogenic positive moment identity in PDF **25 (20), Eq. 2.20** offers a future route to rate/cooling/log-slope/curvature tables within that specific Coulomb model; it does not retroactively certify the current empirical table or add a derivative API.

Next, bind the inventory to caller BBN reservoirs and per-isotope charge distributions; formulate total spectator heat capacity and electron/energy ownership; then add only source-backed missing event components and run matched coupled tests. The existing low-temperature Li proposal remains applicable. Documented inventory coverage is not a claim that all listed reactions are implemented. No source fit, active solver default, running binary, checkpoint, or numerical budget was changed during this read-only intake.

Read scope: overview/contents; PDF 5–13; 22–35; 47–50; 59; 68–69, plus a full-text keyword scan for nuclei/isotopes/molecules. PDF8 was rendered and visually checked. This is a targeted scientific intake, not a claim to have independently proved all 73 pages.
