# BASS_HE → REI IGM F05 원본 26-event H/He·OTS 화학·광자 에너지 수지

2026-11-02 KST. One source-authentic physics unit, Draft/HOLD, no canonical DAG admission.

## Source authority
Parent BASS_HE PR149 immutable HEAD 64e121a1980358134e59b303414c2d54964360de; source REI PR355 HEAD 70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00. Accepted original F05 tick160/131072, 46,080 cells, original source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b, accepted original array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01; original 26-event kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644 and reduced source RHS SHA256 b1f3d6d6397ff727b756816165652a44eb373055256adf7af2e7ef6304ed9b36. Original BASS_HE photo-only result SHA256 d0250b71cc672429ae7da2c043363e8c6b8f0b62c5c59ed8e4f784e40f4c3cf8.

Imported native source 26-event chemical, photo, collisional, recombination and on-the-spot rates. A genuinely original, nuclei-conserving representative interior point of the accepted *component box* was constructed by the original edge.element_conserving_parent_candidate and midpoint logT, then original photon/OTS event operators executed on all 46,080 physical source cells with proper density. This is NOT a proof of membership in the unknown correlated parent state set and NOT a source-accepted trajectory. Separately evaluated original RHS intervals, and 4/4 original-source energy interval reductions contain the point. Fixed original f=0.1 and native v(T); no smooth interpolation invented below 10,000 K.

## Derivation
With epsilon=1.602176634e-12 erg/eV and H/He ionization potentials (13.598434599702,24.587389011,54.41776) eV:
B=epsilon[chi_H*N_HII+chi_HeI*(N_HeII+N_HeIII)+chi_HeII*N_HeIII].
The original 26-event source yields dB/dt=P_photo+P_coll+C_OTS where C_OTS is the recombination/cascade chemical energy rate. Its event ledger defines E_unresolved=-C_OTS-Q_OTS-E_escape, so:
dB/dt+Q_OTS+E_unresolved+E_escape=P_photo+P_coll.
The last equality is an exact *source-defined bookkeeping identity*, not the observed spectrum or a causal local radiation energy equation; no whole-universe photon energy conservation follows. The native gas temperature RHS adds primary photoheat and resolved OTS heat, while original cooling, expansion and particle-change terms remain separate.

## Actual physical outputs (erg/s)
- Photo-only positive binding power: +2.1319571036199573e38.
- Electron-collisional ionization positive binding power: +3.382937732617109e38.
- Recombination/cascade/OTS chemical contribution: -8.244627430174272e39.
- **Net H/He chemical binding energy rate: -7.693137946550565e39.**
- Resolved OTS heat: +1.42203555486775e36.
- Explicit escaped OTS line energy: +2.352070562765713e37.
- Unresolved OTS bookkeeping residual: +8.219684688991748e39.
- Primary native four-group photoheat: +8.22713274931735e37.
- Combined source resolved photo+OTS heat: +8.369336304804124e37.

Actual original RHS interval for net chemical rate [-7.694841173062561e39,-7.690602824089983e39] erg/s, containing source point; original interval OTS unresolved [8.217836116509322e39,8.222352456728345e39], escaped [2.1967170725692446e37,2.352113907535096e37], total resolved heat [8.347136766734664e37,8.381761950137548e37]. This is an evaluation at accepted tick160, NOT a time-integrated tick161 source result.

Native original nine reaction flux categories and six branch parameters were recorded at 46,080 cells in a new compressed CSV; not a replacement source or one of the prior static-opacity maps. Representative original HII case B rate 3.401399713245218e50/s; HeII case B 2.878886570228765e49/s; HeII ground 2.0330793078462289e49/s; HeIII cascade 5.65132393055452e47/s. Native HeII total ionization 1.417386710388729e45/s is largely *collisional*, never a warrant to promote the original G3 subnormal hard-photon current.

**Caution: large unresolved residual is NOT inferred outgoing radiation energy spectrum.** It is defined as leftover source reaction energy and has no angular, spatial, frequency or causal ownership. No primary OTS photon population or source-matched local Jnu was produced. Explicitly separated numerical accuracy, source identity and true radiation closure.

## Comparison with earlier F05 evidence
Frozen point dB/dt times one original native tick (4.87184874916821289e9 s) gives approximately -3.74798044820814e49 erg, which lies in the *NONAUTHORITATIVE tick161* preview interval [-3.7732849134546904e49,-3.7163099410749026e49]. Their midpoint difference is ~0.085%. This agreement is only a directional diagnostic; it is not a valid integrated source-history error bound, not sufficient to prove original v1 2e-4 local gate, and not a canonical admission. REI fast #347 already addresses actual source-integrated full vs twohalf thermal-root energy separately.

## Verification actually executed
- Source-authentic original 46,080-cell 26-event model run exit 0; original 9-rate event graph, OTS source, and temperature/volume time all loaded from SHA-locked unchanged REI PR355 checkout.
- Original nuclei-conserving state and direct three ionization channels; source HI/HeI/HeII collisional split independent recombination rate checks.
- Original source stoichiometry max per-cell scaled residual 7.924766305895325e-16; OTS energy bookkeeping max 1.0968775716317143e-16.
- **Independent second stdlib implementation** reconstructed 9 original reaction rates and 6 branch coefficients across 46,080 cells in 5 energy terms; max per-cell scaled discrepancy 8.6856282548855e-13 versus 2e-12 same-source arithmetic criterion, PASS. Same author; independent-author blind referee NOT_RUN. Wolfram analytically simplified the complete nine-reaction chemical identity to 0; this checks algebra, not source physical completeness.
- Full original-source normal and Python -O optimized cold runs exit 0 and byte-identical output CSV.gz+JSON; independent second algorithm optimized replay byte-identical audit.
- Source-free receipt tests 3/3 ordinary and 3/3 optimized, corrupted JSON negative-case correctly rejected. Exact GitHub Actions science HEAD 841a166e4e62b43acade6731ee2127602bfff73b run #41321592842 SUCCESS; this CI **only** checks publicly published derived receipt, not private original 26event source replay.
- Initial constructor hit original EventFluxResult API shape mismatch (event_rates and chemical_ots_energy_rate_erg_s); repaired new consumer field access only, not original source or scientific tolerance. Host optional NumPy1-binary/NumPy2 dependency import warnings produce stderr but source executed exit 0; environment warnings are separately preserved, not called clean.

Scientific data SHA256:
- 46080-cell CSV.gz f0aba50cf048499ecaed4642b050d2e4c76de9fbe6a77be5d3cc9a3f39ee641c (11,511,550 bytes).
- Science JSON 202c422e7c23da3ea93b82e35429efe387b66225107e94248e28c6263facc5e2.
- Independent reconstruction JSON dce153d7c433d41e476de86b5c63e308a975f48bce98144459ba5df0f94b6220.

## Scope and drift watchdog
One new BASS_HE source-specific original H/He/OTS physical reaction layer, **REI central 28/88_REPORTED, working 33/88_REPORTED, physical fast 4/7_REPORTED, BASS_HE physical 14/18_REPORTED, canonical delta 0**. No source-owner amendment, source clock replacement, native original IVP, versioned official tick161, source-line RT, observed CMB signal, merge, force push, production or tolerance changes. This closes a narrowly measured chemical-energy source composition but does NOT close the central RUX03/04 radiation-source spectrum or F05 canonical admission. STOP producing adjacent source-atlases: next scientific task belongs to the original REI owner causal emission/absorption/OTS spectral-angular photon transport, or original official F05 V2 time integration/14-ledger gate with preserved fail.

Methodology: Mellema et al. (2006) C2-Ray doi:10.1016/j.newast.2005.09.004; Friedrich et al. (2012) coupled H/He OTS doi:10.1111/j.1365-2966.2012.20449.x. Imported papers do not replace REI source authority.
