# BASS_HE next-thread handoff | Fermi ABC measured-gamma source extension

```ini
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
CURRENT_PR=117
CURRENT_HEAD=RECHECK_REMOTE_FINAL_SHA
PARENT_PR=116
PARENT_HEAD=93173f3c73f53e114616f524be73000688ab432b
BASE_BRANCH=research/he-dd-fermi-igrb-exfor-observed-photons-20261030
BRANCH=research/he-dd-fermi-abc-original-bins-20261030
ROOT=research/he_dd_fermi_abc_original_bins_20261030
CENTRAL_DAG=28/88
HE_DAG=14/18
PREVIOUS_OBS_GAMMA=2/4_SCOPED_UNCHANGED
FERMI_ABC_AUX=3/4_SCOPED
PHYSICAL_DELTA=0
INDEPENDENT_R6_C9=NOT_RUN
kappa=null
R_event=null
heat_rate=null
physical_activation=false
L4=false
production=HOLD
```

## What is actually new

Pinned Fermi 2015 78-row 26 A+26 B+26 C Table3 public mirror Git blob 794cb6fcbef243be950613475c4254d6ab3877a4, local full bytes 15975 with SHA256 a78ced8234a7eb104a5f5b406a6bc609591ec2c323a26008625b239b5dccc0e5. **Original CDS raw bytes NOT acquired**. Exact 200–282.8 and 282.8–400 MeV integrated intensity source six rows (model A/B/C), BASIC uncertainty includes statistical PLUS instrumental systematics, FG separate. Original EXFOR M0475003 reported six SIG points 201/225/253/285/320/359 MeV with physical rest-energy Q=23.84647820 MeV, no measured total SIG330.

Two intra-bin assumptions: flat and model-specific *IGRB fitted PLE* with A/B/C gamma 2.32/2.28/2.26, cutoff 279/206/233 GeV, renormalized within actual bin. Use of IGRB PLE shape on EGB is EXTRA. 3 models × 2 components × 2 assumptions = 12 source-reported-rate-like and born-K-like outcomes. Preserve positivity of EXFOR knot coefficients and source-specific uncertainty components; never sum IGRB+EGB. Wolfram flat rational analytic corroboration and 20 Python tests PASS. Main result IGRB flat A2.058528236e-38 B2.212214564e-38 C1.743559851e-38 s^-1 He^-1; IGRB PLE A2.229056993e-38 B2.393631184e-38 C1.884069870e-38. Neither is measured nuclear event rate.

## Exact current source and tests

- Run `python -m unittest discover -s tests -p 'test_*.py' -v` and `python src/fermi_abc_exfor.py --root . --out results` in extracted package.
- Source info `data/SOURCE_MANIFEST.json`. Verify Git mirror blob and local byte SHA. `data/fermi_igrb_2015_AB_C_78row_mirror.csv` is full preserved Git-mirror bytes, not original CDS bytes.
- Computational statement `notes/THEORY_KO.md`, report `notes/REPORT_KO.md`, contract `notes/IMPLEMENTATION_CONTRACT.json`, executable `src/fermi_abc_exfor.py`, numeric JSON and CSV `results/`.
- Source branches: PR116 immutable parent, PR114 distinct low-E sister, BASS CE1-S PR262 and REI PR274 context only. No merge/force/physical DAG inflation.

## Next physical action

1. Acquire original CDS Table3 raw `table3.dat` and byte-compare against mirror (D4 original-source authenticity).
2. Obtain Arends/Silverman original actual detector acceptance, efficiency, event/inclusive normalization, 330-MeV exclusive total SIG (if possible); do not invent missing data.
3. Source-qualify gamma f_gamma(x,p,z) 200–400 MeV in *proper He target frame*, not simply present observer IGRB, including resolved-source anisotropy and gamma attenuation. BASS Liouville model sky is geometrical but not this input.
4. Construct named D_fast Coulomb stopping/ionization/nuclear redistribution and secondary heating/escape, gas C_V; evaluate actual energy conservation and propagated history. No current heat claim.
5. Do not rerun historical IVPs or 4501-node LP. Native distinct-author R6/C9 NOT_RUN.

Backup receipts: consult new STAGE_LEDGER.json and DELIVERY_RECEIPT.md. Google Drive and Dropbox text ACKs are not full ZIP dual binary restore. If publication blocked, preserve local ZIP/Library and state exact blocker.
