# REI UVB six-moment source-response · final next-thread handoff

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rei_bianchi
CURRENT_PR=261
CURRENT_BRANCH=research/rei-uvb-six-moment-response-20261029
READ_CURRENT_PR_HEAD_BEFORE_WORK=true
PARENT_PR260_HEAD=7438e2e85e8f0ecb03292558280521bbf58e707d
VERIFIED_SOURCE_SCIENCE_COMMIT=363518a9161e4a88912de97b978639439b1790aa
VERIFIED_STAGE_C10_COMMIT=acd77bf2e1b3314749531cfdc6c9829034267f70
VERIFIED_SOURCE_91_CELL_READBACK=800f03215372e54a92e1278dd004dd859a7f5eae
ORIGINAL_DAG_WORKING=33/88
ORIGINAL_DAG_CENTRAL_LAST=28/88
ORIGINAL_DAG_DELTA=0
UNIT_STAGE_PROGRESS=18/20
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
NO_MORE_IVPs=true
AUTO_NEXT_NODE=false
F4=PARTIAL
L4_ready=false
actual_REI_temperature=null
actual_native25=null
physical_radii=null

FROZEN_SOURCES:
BB13_SHA256=13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b
P19_13_ROW_PROJECTION_SHA256=dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff
P19_ORIGINAL_59_ROW_GIT_BLOB=218d81f68447da438228a7b102e1cec96a8e8a1a
P19_13x7_NUMERIC_SOURCE_COMPARISON=91/91_MATCH

SCIENCE:
R_X(z;a)=R_X^P19(z)*10^[beta+kappa(z-3.6)]
D_a R_X=ln(10)*R_X*[1,z-3.6]
D_a^2 R_X=ln(10)^2*R_X*t*t^T
h_Uq(t)=t^T c+||G^Tt||_1+sqrt(q t^T V t)
Pointwise rate bounds=P19*10^[t^Tc +/- (||G^Tt||_1+sqrt(q t^TVt))]
q1=3.8414588206941236, q2=5.991464547107982
SOURCE_DOMAIN=2.4<=z<=4.75
SIX_MOMENT_COMMON_SCALE=MODEL_ASSUMPTION_NOT_SIX_OBSERVATIONS
SPECTRUM_LI_CR_NUCLEAR_RATES=NOT_SUPPLIED
P19_KNOT_DERIVATIVE=ONE_SIDED
z20_PREHISTORY=MISSING
Bianchi_directional_zobs_to_zmean=NOT_BOUND

FIXED_TARGET_PORTS:
P_X=y_X Gamma_X events/Href/s
Q_X=y_X heat_X eV/Href/s
absorbed_photon=I_X P_X+Q_X with supplied I_X
D_a_y_X=UNKNOWN, do not treat fixed-y Jacobian as physical trajectory.
Mean x=ln(a/a_ref), dz_mean/dx=-(1+z_mean).
BASS_PR234 d tau/dx=K ne/H;
D_a tau_rhs=K/H D_a ne-K ne/H^2 D_a H;
K physical value, D_a ne, D_a H, chemistry J_R and tangent IC/BC all unbound.

VALIDATION:
Python source-rate worker exit0; 21/21 new tests PASS.
Independent QR, 256 q0 corners at 3 z, q2 ellipsoid, MP80 clock,
Jacobian/Hessian finite differences, photoenergy, domain controls PASS.
Corrected Wolfram five zeros and True; original symbolic-precedence
and binary64-FD failures preserved. Different-author R6/C9 NOT_RUN.
No original GLS/17-state IVP/physical solver/plot rerun.
Prior repo-wide CI PR260 cargo fmt FAIL, cargo test SKIPPED.

PUBLICATION_AND_BACKUP:
Draft PR261 stacked on PR260; no merge, no force.
20 separate stage checkpoint Git commits, 20/20 Git stage readbacks.
Nine core source/code/result blob identities match local bytes.
20 stage ZIPs independently SHA/CRC verified inside master ZIP.
MASTER_ZIP=REI_SOURCE_RESPONSE_FULL_20261029_3e1fcbdc.zip
MASTER_BYTES=263221
MASTER_SHA256=3e1fcbdc0e88e22be9c8fddbcdd21e12fa98250814d39721c671ed299f049f0c
Both Google Drive and Dropbox master ZIP upload ACK and size263221 readback.
Not 20 individual provider ZIP ACKs. Remote whole-byte SHA NOT_RUN.
Old closed resource grants not reset, global resource PASS NOT_CLAIMED.

NEXT_DAG:
Read NEXT_DAG_CONTRACT.json in PR261. Seven-node overlay includes
UVB_RATE6_PORT (scoped, independent R6/C9 held), physical clock,
chemistry tangent, tau tangent, CMB observable and error enclosure.
Only act on genuinely source-bound available inputs; do not auto-run IVPs,
merge PRs or promote F4/L4/native25. Obtain distinct-author R6/C9 first.
```
