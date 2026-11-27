# BASS_HE 다음 연구 스레드 handoff: HE_EXFOR_DETECTOR_EVENT_SEMANTICS

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PR=107
BRANCH=research/he-dd-reciprocity-20261029
HEAD=READ_LIVE_BRANCH_REF_AND_PR_BEFORE_ANY_MUTATION
E1_SCIENCE_COMMIT=2a5718181ed5e69a2f26ff8d8536f80ce865c6c4
ROOT=research/he_dd_reciprocity_20261029
NEW_ROOT=research/he_dd_reciprocity_20261029/experimental_semantics_20261029

Read NEW_ROOT/REPORT_KO.md, src/experiment_semantics.py,
tests/test_experiment_semantics.py, BRIDGE_CONTRACT.json,
evidence/SOURCE_EVIDENCE.json, DELIVERY_RECEIPT.md.
Read original ROOT/THEORY_KO.md, REPORT_KO.md,
IMPLEMENTATION_CONTRACT.json, RESULTS.json,
STAGE_LEDGER.json, DELIVERY_RECEIPT.md.

CENTRAL_DAG=28/88
HE_DAG=14/18
PR105_DAG=2/2
PR106_DAG=1/2
RECIPROCITY_DAG=1/2
WORKFLOW=18/20
ORIGINAL_NATIVE_R6_C9=NOT_RUN

EXFOR_SOURCE=IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4
EXFOR_PREVIOUS_SHA256=b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f
EXFOR_GIT_BLOB=c49433293921dbb012d7f1b0387745732a598efa

NOW_VERIFIED_FROM_EXFOR:
  Arends M0475001: tagged bremsstrahlung, liquid helium cylinder,
  COINC+TOF+SCIN, both outgoing d1,d2 coincident in two spectrometer arms,
  measured each mass+energy+angle and rejected accidental coincidences.
  DA at E_gamma 213 MeV, CM73deg 0.41+-0.09 nb/sr;
  DA at E_gamma 330 MeV, CM73deg 0.07+-0.05 nb/sr.
  Statistical ERR-S, no 330 MeV SIG.
UNVERIFIED:
  original paper full texts; absolute detector efficiency and acceptance;
  event/particle counting and hemisphere/full-sphere factor;
  photon and deuteron polarization states; inverse raw DA source row;
  same-s and same-angle measurement with experimental bin resolution;
  photon history in alpha-target frame; n_alpha,U_alpha;
  D_fast spectral pool, stopping/deposition/Cv.
SILVERMAN:
  Td376MeV, CM gamma angles 73/91, abstract ratios 2.0+-0.9/1.7+-0.9.
  E_gamma_equiv=213.12551760977376MeV, NOT E_gamma330MeV.
  Neither abstract ratio nor a 1985 dp->3He gamma Td600 paper is dd inverse DA.

E1_GITHUB_NEW_COMMIT=2a5718181ed5e69a2f26ff8d8536f80ce865c6c4
E1_CODE_BOUNDED_TESTS=26/26_PASS
E1_DRIVE_STAGE_ACK=SUCCESS_AND_READBACK
E1_DROPBOX_STAGE_ACK=SUCCESS_AND_READBACK_REV21
E1_DRIVE_REPORT_ID=1rpLEMZZlRCm4BQHIpInTnTZGmnYRPFr90FFf5gesoKk
E1_DROPBOX_REPORT_ID=id:BSpOijBcT10AAAAAAEHVJg

NEXT_PHYSICAL=ORIGINAL_EXPERIMENT_DA_MULTIPLICITY_EFFICIENCY_POLARIZATION
  1. Get Arends 1976 Phys Lett B62 411 and Silverman 1984 Phys Rev C29 35
     whole original text/preprint including tables, detector acceptance,
     coincidence/efficiency formulas, polarization and DA conventions.
  2. Find source-qualified reverse raw DA at EXACT same s and matched CM
     angle, or explicitly model resolution/angle interpolation as uncertain.
  3. DO NOT assign kappa=1 or 2 from coincidence metadata or abstract ratio.
  4. Attach actual n_gamma(E,Omega,x,t) in alpha rest frame, not frozen
     IGM photon-per-H surrogate; then n_alpha,U_alpha and correlated d daughters.
  5. Separately integrate named D_fast slowing/deposition/Cv after sources pass.
  6. No old completed IVPs or existing science suite rerun.
  7. Native independent R6/C9 only with actual distinct reviewer/run.

R_event=null
physical_activation=false
L4=false
production=HOLD
No central/HE/PR106/reciprocity node increments until physical source gate passes.
No force push, no merge; record actual Git SHA and provider ACK/readback.
```
