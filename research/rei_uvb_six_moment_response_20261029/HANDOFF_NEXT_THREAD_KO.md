# REI 다음 스레드 복사형 handoff · 2026-10-29

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/rei_bianchi
PR260_PARENT_HEAD=7438e2e85e8f0ecb03292558280521bbf58e707d
UNIT=REI_UVB_SIX_MOMENT_SOURCE_RESPONSE_20261029
FROZEN_BB13_SHA256=13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b
P19_PARENT_GIT_BLOB=218d81f68447da438228a7b102e1cec96a8e8a1a
P19_13_ROW_PROJECTION_SHA256=dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff
WORKING_DAG=33/88
CENTRAL_LAST=28/88
ORIGINAL_DAG_DELTA=0
UNIT_PROGRESS=18/20
R6_DISTINCT_AUTHOR=NOT_RUN
C9_DISTINCT_AUTHOR=NOT_RUN
F4=PARTIAL
L4_ready=false
actual_REI_temperature=null
actual_native25=null
physical_radii=null
NO_MORE_IVPs=true
AUTO_NEXT_NODE=false

SCIENCE:
R_X(z;beta,kappa)=R_X^P19(z)*10^[beta+kappa(z-3.6)]
D_a R_X=ln(10)*R_X*[1,z-3.6]
D_a^2 R_X=ln(10)^2*R_X*t*t^T
h_Uq(t)=t^T c+||G^T t||_1+sqrt(q t^T V t)
pointwise R_X bounds=P19_X*10^[t^Tc +/- (||G^Tt||_1+sqrt(q t^TVt))]
DOMAIN=z in [2.4,4.75], 13 source knots, six H/He moments only.
COMMON_SCALE_SPECTRAL_SHAPE=ASSUMPTION_NOT_OBSERVATION
JOINT2_95_COVERAGE=CONDITIONAL_GAUSSIAN_KNOWN_C
DIRECTIONAL_BIANCHI_REDSHIFT=NOT_BOUND
z20_SOURCE_PREHISTORY=MISSING
fixed_y_event_port=y_X*Gamma_X; fixed_y_photoheat=y_X*heat_X
absorption_energy=I_X*y_X*Gamma_X+y_X*heat_X
physical_D_a_y_X=MISSING
mean_x_clock=ln(a/a_ref), dz_mean/dx=-(1+z_mean)
BASS_tau_source_row=K*ne/H
D_a_tau_rhs=K/H*D_a_ne-K*ne/H^2*D_a_H
physical_D_a_ne=D_a_H=K_value=UNBOUND

EXECUTION:
python -B code/run_once.py
python -B -m unittest discover -s tests -v
new 21/21 PASS, independent QR, MP80 mean-clock, CAS corrected.
No original GLS/17-state IVP/physical suite rerun.
Repository-wide historical CI cargo fmt FAIL and cargo test SKIPPED.

NEXT:
1. Inspect latest PRs and read this unit's Git publication and per-stage
   Drive/Dropbox receipts before importing any science.
2. Request genuinely separate-author R6/C9 source+code review.
3. Bind actual BASS source K/ne/H, chemistry J_y,J_R and initial S,
   directional redshift and error/norm identities before optical tau claim.
4. Preserve original 33/88, 28/88, F4/L4, budgets, old failures and source.
5. No force push, merge, production activation or new IVP without authorization.
```
