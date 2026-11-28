# BASS_HE conditional Rice P2 daughter pair covariance | next-thread handoff

```makefile
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=127
PARENT_HEAD=b1733cc18180eeffc90a5ce5eac9ff2feab90d36
SOURCE_PR126_HEAD=3305c4579221edde36c14f941b3530375aca4f7a
NEW_UNIT=RICE2000_SIN2_CONDITIONAL_DPAIR_ANTICORRELATION
OUTPUT_ROOT=research/he_dd_rice2000_sin2_cov_20261030
NEXT_CANDIDATE_ONLY=ACTUAL_HE_REST_150_250_MEV_PHOTON_HISTORY_AND_DFAST_STOPPING
AUTO_NEXT_NODE=false
CENTRAL_DAG=28/88
HE_PHYSICAL_DAG=14/18
RICE_BIRTH_AUXILIARY=1/2
RICE1998_SOURCE_RECONCILIATION=2/2
CONDITIONAL_MODEL_AUX=1/1_SCOPED
CANONICAL_PHYSICAL_DELTA=0
SOURCE_RICE2000_TABLEI_GIT_BLOB=9cdec4449b22bdba2797bbdfb815e98901b85636
SOURCE_RICE2000_TABLEII_GIT_BLOB=378359462ef0c32ae6c7b5de6105bce9a8f7d8aa
R06_DISTINCT_AUTHOR=NOT_RUN
C09_DISTINCT_AUTHOR=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
kappa=null
R_event=null
heat_rate=null
L4=false
PRODUCTION=HOLD
NO_MERGE=true
NO_FORCE_PUSH=true
```

## Scoped physical output

Input Rice 2000 Table I 12 real DCS (1 experiment), Table II constrained endpoint-zero P0+P2 author fits sigma_tot=8.29 nb (150-190MeV), 4.34 nb (190-250MeV). The finite detector geometry correction Q_k means a2 alone is not true angular moment. *Extra unverified per-E model M1:* every E in bin has a normalized w(mu)=3(1-mu²)/4, hence angular second moment A=1/5. For all nonnegative **event-energy** weight ν(E) on each respective bin,

Cov(K+,K-)=Varν(E)/4 - (1/5)Eν[Delta(E)^2], where Delta=E/2 sqrt(1-4md²c⁴/s_E), s_E=(Malpha c²)²+2(Malpha c²)E.

Sharp supremum covariance for 150–190 MeV is **−4.6358115624 MeV²**, for 190–250 MeV **−5.2589395532 MeV²**; model-conditional and not empirically measured covariance. Exact criterion Acrit=0.1908413582, 0.1952331575. Threshold100MeV single-D fraction bounds in two Rice bins: [0,0.0916327650], [0.0916327650,0.7317248702]. Daughter multiplicities are twice these numbers per real nuclear event. Results tables are model-derived, not new experiments or heat measurements.

Original source and independent-candidate literature: Rice et al PRC61 064612 (2000) DOI 10.1103/PhysRevC.61.064612. J. G. Asbury and F. J. Loeffler, *Physical Review* 137 B1214 (1965), DOI 10.1103/PhysRev.137.B1214, 221/265 MeV angle 45 lab, need primary numeric table/EXFOR entry. C. F. Williamson, J. Boujot, J. Picard *Tables of Range and Stopping Power of Chemical Elements for Charged Particles of Energy 0.5 to 500 MeV*, CEA-R-3042 (1966), INIS https://inis.iaea.org/records/9k4kt-wkn64; request corrected deuteron projectile H/He pages, NOT an ionized-plasma stopping calibration. Bryan J. Rice Duke PhD (1998), UMI 9825640; source Table5.2 excerpt was already supplied PR127; still need detector acceptance/energy-angle covariance from complete original.

## Execution and restore

In archive root run `bash REPRODUCE.sh`. Validates Git blob SHA of both raw numeric source inputs; 13 conditional physics tests; source CSV/JSON reproducible output. Previous PR127 baseline 19/19 PASS independently restored. New physics phase did not generate actual helium-rest photon history or plasma Dfast stop. Need observer-covariant f_gamma(x,p), nalpha and U_alpha, cross-section per E/angle with detector response, plasma stopping and escape/time delay to evaluate actual R_event and heat. Do not substitute Fermi IGRB (other epoch) or HE E13C1 13.7-100eV test fixture.

## Durable receipt

Consult `DELIVERY_RECEIPT_KO.md` in archive or PR for actual GitHub PR number/head and confirmed Library/GoogleDrive binary readback after publication. Do not infer from this handoff that external upload or review was completed; receipt is authority.
