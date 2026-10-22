# Display-only addendum: logarithmic ordinates and dual physical coordinates

The user requested more readable logarithmic y axes and both redshift and elapsed time in Myr on x axes. `DISPLAY_CONTRACT.json` is the frozen executable specification. It applies to the 28 base and seven strong-stress figure designs, in PNG and PDF. The archived 18 reference figures remain unchanged. No IVP, nuclear postprocessing or new physical source calculation is authorized or required.

## Abundance ordinates

Keep the directly stored `log10(Y)` plotting coordinates because some nuclear inventories cannot safely be exponentiated in ordinary floating point. Format an ordinate value k as the physical abundance tick `10^k` and label it `Y=n_species/n_B (log scale)`, or its ionic analogue. This is a logarithmic abundance display; applying an additional log transform would be an error. Zero inventories cannot appear on a log ordinate and remain explicitly annotated. The unresolved neutral/ionized T partition remains blank, not zero.

Signed conditional-fraction differences, shear, P_m, P_r, photon/neutrino stresses, H/H_reference-1 and signed control residuals use base-10 symmetric logarithmic axes. Preserve the zero line and both signs. State the linear-region transition. For fraction-difference panels it is 3.3929270504273745e-9, chosen from the previously recorded comparison scale solely as a display convention. It is not an error band, subtraction or certified noise floor. For other signed panels and control residuals, use two decades below the panel's maximum absolute magnitude, rounded to a power of ten. All-zero panels are labelled explicitly.

Strictly positive geometry values use ordinary log ordinates. Exact zeros in nonnegative quantities are omitted from that logarithmic ordinate with a clear annotation rather than replaced by a made-up positive floor.

## Dual axes without a false common clock

The primary x axes remain linear: redshift covers 20 to2 and proper elapsed time begins at zero. Logarithmic x offers no necessary advantage for these ranges and would exclude the initial time. One displayed Myr equals 1e6 Julian years, each 365.25 days. Physical elapsed-second data remain unchanged.

For redshift-based panels, retain each trajectory's actual saved z coordinate and add an upper elapsed-Myr axis from the group's reference case. For time-based panels, use each trajectory's own saved proper elapsed time in Myr and add an upper redshift axis from that reference case. Label the auxiliary axis as a **reference clock**, state the exact reference case in the figure, and explain that other cases have different z(t).

The five base groups use `quotient_L16_S0_Am0_Ar0`. The strong-stress group and its control comparison use `strongPiM_m3_f0.3_Pi0_L16`. A single scalar-reference mapping does not become the physical clock of all curves merely because it appears on the same plot.

Construct readable upper-axis ticks by monotonic piecewise-linear interpolation of those actual 257-sample histories. Reverse descending z before interpolation as needed. Place ticks only within the reference's saved support; do not extrapolate or clamp out-of-range values. A time trajectory extending beyond the reference endpoint may continue without corresponding extra upper-axis ticks. No additional background solution is needed.

This explicitly supersedes the earlier blanket ban on a shared secondary time axis **only for a clearly disclosed reference-clock axis**. The ban on falsely representing one case's clock as every case's clock remains in force. It also replaces Gyr display units by Myr. All scientific selection, matching and measured-response claims remain unchanged.

## Finite verification and stopping rule

Check finite monotonic reference coordinates, endpoint and saved interior-knot interpolation, correct Myr conversion, preservation of the original plotted data and all 35 designs. Confirm that signed plots retain signs and zero, abundance coordinates are not logged twice, and top-axis labels do not overlap facet titles. Shared subplot layouts may place upper ticks only on the top row of each column, provided the figure-wide reference-clock note remains clear.

Inspect representative abundance, ionic, tiny-difference, signed-context and strong-control figures. One render pass plus at most one targeted display repair completes this addendum; do not convert this presentation change into another physical experiment or convergence campaign.
