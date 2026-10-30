# REI F4 | Li II measured 2E1/M1 photon source-capacity handoff

Use `$physmath-research-loop $scispace $exa $wolfram`. This is scoped output after parent PR279, not full F4 release.

```makefile
PROJECT=cosmosapjw-quantum/rei_bianchi
PARENT_PR=279
PARENT_HEAD=46d7d3192c32a069ef2b6d9aa5b7202e9c2bfa78
BASS_OWNER=cc602e209e7deeb511ab2a1f3b2268d55206c43c
PR279_FULL_SHA256=6e50586131ab6f8f76b72ee8c7125dfd3225211d528609c862e01a305a0ab6d3
CURRENT_UNIT=REI_BASS_LI1S_MEASURED_RADIATIVE_CAPACITY_20261030
CURRENT_PR=SEE_FINAL_ACK
CURRENT_HEAD=SEE_FINAL_ACK
UNIT_STATUS=1/1_SCOPED_PHOTON_CAPACITY_NOT_FULL_F4
NEXT_NODE=REI_LI1S_SOURCE_QUALIFIED_TWO_PHOTON_DIFFERENTIAL_AND_CASCADE_TRANSPORT
AUTO_NEXT_NODE=false
SOURCE_EPOCHS=193
ORIGINAL_LI1S_BIN_ROWS=8492
THRESHOLD_CELLS=25476
NEW_IVPS=0
PYTHON_TARGETED=28/28_PASS
WOLFRAM_SYMBOLIC=ZERO_RESIDUAL
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
WORKING_DAG=33/88
CENTRAL_DAG=28/88
F4_FAST_DAG=4/7
CANONICAL_PHYSICAL_DELTA=0
F4=PARTIAL
L4_ready=false
NO_MORE_IVPS=true
NO_MERGE=true
NO_FORCE_PUSH=true
PRODUCTION=HOLD
```

Restore `REI_F4_LI1S_RADIATIVE_PHOTON_20261030_FULL.zip`; execute `bash VERIFY.sh` and inspect `results/RESULT.json`, `THEORY_KO.md`, `REPORT_KO.md`. The archive nests the exact PR279 full archive and upstream PR277 source. Distinguish stable source data from later independent PR278 frozen-equilibrium diagnostics.

Scientific results: measured Li II singlet 503±26 μs 2E1, triplet 52.2±5.0 s M1; original 8492 Li6I/Li7I source event rows; 193 epoch photon number/energy outputs; 25,476 threshold-capacity cells. H/HeI 1..2 and HeII 0..1 threshold photons per permitted event (forced triplet yields HeII 1). Integrated conditional vacuum H/HeI `[3.4426556153e-11,6.45776317596e-11]`, HeII `[4.27548054649e-12,3.4426556153e-11]` per baryon. No branch probabilities or two-photon spectrum assumed.

Next useful scientific actions (no autonomous next-node execution): find **original source-qualified 2E1 differential spectrum** `dA/dE` for heliumlike Li II and measured/sourced Li K-shell singlet/triplet partial yields, then compute *actual* source-weighted H/He threshold photon counts; subsequently conditional radiative transfer and nonthermal electron deposition under consistent full REI/BASS chemistry and clock. If sources unavailable, preserve the current sharp bounds; do not invent heats, photon absorption, Auger yields or temperature response. Keep full chemistry and clock obligations separate. No new IVPs, observational tau/CMB promotion, merge or force push.
