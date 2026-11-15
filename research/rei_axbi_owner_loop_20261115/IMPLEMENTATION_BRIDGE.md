# R9 — definition, computation and reusable implementation

| Defined object | Computational form | Implementation and output | Validation status |
| --- | --- | --- | --- |
| H/He/electron state | x_HI=1-x_HII; x_HeI=1-x_HeII-x_HeIII; n_e=n_H x_HII+n_He(x_HeII+2x_HeIII) | `validate_frame`, `load_case`; `abundances.csv.gz` | All actual saved rows; normalized charge <=2.23e-16 |
| Baryon-number abundance | Y_i=n_i/(n_H+4n_He) | `load_case`, six Y columns | Original PR129 census reused; current normalization checked |
| Equal-scale response | X_q(a)-X_0(a) | `comparison_zbar.csv.gz`; 3003 rows | Source interpolation/domain and coordinate retention verified |
| Equal-elapsed-time response | X_q(a_q(t))-X_0(a_0(t)) | `comparison_time.csv.gz`; 3003 rows | Separate scalar bisect computation checks every row and seven observables |
| Clock decomposition | Delta_t=Delta_a at a_q + reference displacement | Same table with both terms, both a/z coordinates and common t | Fraction residuals/arithmetic checked; no coupled SAME_H claim |
| Background clock offset | Integral of -r²/[H_F sqrt(1+r²)(sqrt(1+r²)+1)] dln a | `clock_offset`; `clock_check.csv` | Wolfram exact algebra; independent 60-digit reciprocal integration |
| HII milestone | First consecutive upward native-row bracket, linear-ln(a) crossing | `milestone`; 12 rows in `milestones.csv` | Separate scalar reader; local PCHIP sensitivity retained, not an evolution bound |
| REC proper collision rate | Gamma_T=c sigma_T n_e in physical seconds | `thomson`; 4004 rows in `thomson_segment.csv.gz` | Independent native-time integral; positive conditional probability sum |
| BASS geodesic relation | Conserved covariant spatial momentum, tetrad energy | `method_checks.py` on original a,b samples | 104 geometry points; <=5.56e-16 relative energy difference |
| Original angular quadrature | GL8 positive low-order moments | `method_checks.py` | Original rule checked; different donor midpoint correction not applied |

## Next consumer action after a real +0.01 completion

Use `SHEAR_PLUS_RECOVERY_CANDIDATE.json` as the concrete source/clock/budget
handoff. That file is a recovery candidate, not a completed history or a
new execution receipt. Once a new bounded recovery segment actually reaches
zbar4, compose the predecessor, retained segment and new segment exactly
once, preserving the abandoned post-checkpoint tail separately. Obtain a
new completed-case manifest and hashes before touching the consumer inputs.

Add the real completed SHEAR_PLUS case to a newly versioned input manifest.
The present four-case release and its `all_five_signed_cases_complete=false`
remain immutable. A future release must derive any five-case completion
from all five actual manifests and source/clock/row checks; simply flipping
that output flag is invalid. Reuse the four verified histories and all
unchanged source evidence. There is no need to repeat the all-repository
survey or rerun those four coupled histories solely to change executor.

Then execute the previously defined AX11 refinements and AX12 variants with
their own preserved cumulative budgets. The new comparisons here provide
concrete response magnitudes, milestone brackets and coordinate choices
for that work. They do not replace a genuine paired evolution-error study.

For a future scalar response claim, specify which matching is intended:
fixed mean redshift, fixed elapsed proper time from the selected initial
surface, or a new observer/redshift mapping. Carry that choice into the
error norm, figure labels and reported milestone shifts.
