# BASS_HE next thread | source-exact angular deuteron response

```ini
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=118
PARENT_HEAD=d92e94290977d4f0bb59ea16c8219d52a295bd99
NEXT_PR=READ_LATEST_REMOTE
NEXT_HEAD=READ_LATEST_REMOTE
ROOT=research/he_dd_fermi_angular_pair_20261030
CENTRAL_DAG=28/88
HE_PHYSICAL_DAG=14/18
PR117_ABC_DAG=3/4_SCOPED
PR118_HIGHLAT_DAG=2/3_SCOPED
NEW_ANGULAR_DAG=2/3_SCOPED
PHYSICAL_DELTA=0
R6_C9_NATIVE_DISTINCT_AUTHOR=NOT_RUN
kappa=null
R_event=null
heat_rate=null
L4=false
physical_activation=false
production=HOLD
```

**Exact sources:** IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4, original 3349B SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f. Fermi public Git mirror 15975B SHA256 a78ced8234a7eb104a5f5b406a6bc609591ec2c323a26008625b239b5dccc0e5, Git blob 794cb6fcbef243be950613475c4254d6ab3877a4; original CDS official file raw bytes not certified.

**Actual output:** `sources/` exact mirror, `src/angular_injection_atlas.py`, `tests/test_angular_injection.py`, `results/MEASURED_ANGULAR_DPAIR_12.json`, `ANGULAR_DPAIR_FERMI_168.json` and CSV, `notes/THEORY_KO.md` and `REPORT_KO.md`. Note 168 are CONDITIONAL modeled photon × 12 measured DA rows, NOT 168 independent observational measurements.

Reproduce in ZIP extracted root: `python src/angular_injection_atlas.py --root . && python -m unittest discover -s tests -p 'test_*.py' -v && python -m compileall -q src tests`. Preserve source SHA/Git blob, original source rows, true Fermi energy bins and `sr_sky` vs `sr_CM` distinction. Do not replace 330 measured DA with nonexistent 330 SIG. `R_event` and thermal heat remain null. Git Cloud/Drive/Dropbox backups must each have their own acknowledgements and byte readback if claiming full ZIP restore.

**Next physically useful node:** obtain original detector efficiency/coincidence polarization and exclusive event convention from Arends/Rice; resolve current local He-rest high energy gamma phase-space f_gamma(t,x,p) including attenuation and redshift, then actual nonthermal D pair transport (ionization, Coulomb/nuclear redistribution, secondary deposition, escape) with C_V. No auto-merge/force push, no production/L4 promotion until source-verified evidence. Native independent review NOT_RUN, original Rice numeric twelve points NOT_ACQUIRED.
