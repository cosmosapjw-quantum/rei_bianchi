# 다음 rei_bianchi 연구 스레드 인계 (2026-10-29)

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rei_bianchi
PARENT_PR=261
PARENT_HEAD=8a3107a6477a648ad87a4db2a52240c1bea4cc42
UNIT=REI_UVB_SAVED17_SOURCE_TANGENT_20261029
NEW_REVIEW_BRANCH=READ_ACTUAL_GITHUB_PR_AND_HEAD

ORIGINAL_WORKING_DAG=33/88
CENTRAL_LAST_OBSERVED_DAG=28/88
ORIGINAL_DAG_DELTA=0
NEW_SCOPED_STAGE=18/20
R6_DIFFERENT_AUTHOR=NOT_RUN
C9_DIFFERENT_AUTHOR=NOT_RUN
F4=PARTIAL
L4_ready=false
ACTUAL_REI_TEMPERATURE=null
ACTUAL_NATIVE25=null
PHYSICAL_RADII=null
NO_MORE_IVPS=true
AUTO_NEXT_NODE=false

ORIGINAL_MODEL_BLOB=1f8d7965fe286a4ed78ea6bbfcc38178aafe8adc
ORIGINAL_ON_REFINED_CSV_BLOB=189c2d903e25c18bee49e0ab6add3ba1d1805e93
SAVED_7_ROWS_NUMERIC_FNV1A64=174743cb945f8bfe
SAVED_7_ROWS_SHA256=7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77
PARENT_BB13_SHA256=13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b
PARENT_P19_PROJECTION_SHA256=dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff

NEW SCIENCE:
Seven H1/D/T/He3/He4 photoionization events, 17 heavy-state populations.
F_UVB=S diag(E*y) P R6, J_y^UVB=S diag(P*R6) E,
J_R^UVB=S diag(E*y) P (17x6),
D_a F_UVB=ln(10) F_UVB outer (1,z-3.6) (17x2).
A17^T S=0, Q17^T S=ones(7), mu1(J_y^UVB)=0.
Single-z B_a rank<=1, seven saved-z stacked B_a rank=2.
Actual frozen saved z=[2.404494,2.789073,3.217095,3.603020,4.024262,4.378370,4.701690].
Source-only electron/Href/s at z3.603019593287379=3.429774458100496e-16.
Conditional joint2-95 source envelope at this saved z:
[2.383266e-16,5.076625e-16] electron/Href/s.

VERIFICATION:
New Python tests15/15 PASS; independent direct-event C++20 seven rows PASS;
max C++ component relative3.251e-16; Wolfram symbolic4 residual zeros.
Selected 7x17 values numeric content verified vs original Git blob at 17 significant digits.
No IVP, no old GLS replay, no rendering.

IMPORTANT:
- The saved ON_refined state is from the OLD uncalibrated prescribed bath.
- The new source is a COUNTERFACTUAL INSTANTANEOUS forcing on frozen states.
- The result is NOT D_a y(t), D_a n_e(t), full chemistry J_y, physical tau,
  a 17->30 state lift, Bianchi directional redshift or physical error radius.
- P19 photoheating is an energy port; do not automatically book it twice.
- No Li rates, nuclear/CR/hard-photon/stopping source inferred from HI.
- Keep original source budgets closed; unknown overhead UNKNOWN_NOT_ZERO.

NEXT EXECUTABLE:
1. Read actual new PR/HEAD and the source/test/receipt identities.
2. Obtain truly different-author R6/C9 review of new source extraction,
   isotope approximations, event energy ownership and code.
3. Seek actual full source-accepted chemistry J_y (including electron feedback),
   physical density nHref and clock H, and tangent initial/boundary conditions.
4. Only then construct a conditional causal variational solution or rigorous
   enclosure for D_a y and D_a n_e, followed by BASS PR234 tau consumer.
5. Do not promote 33/88, F4/L4, global Bianchi tilt or observables on
   this source-only result; no automatic new IVP or old campaign replay.
```
