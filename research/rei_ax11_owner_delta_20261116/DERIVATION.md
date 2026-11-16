# Saved-history photon, event and energy accounting

## Definitions and source

The source is the original17-file AXBI corpus
`d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`.
`axbi_driver.rs::{Ledgers,ledger_values,binding,total_energy,residuals}`,
`igm_thermal.rs::igm_thermal_rates` and `igm_state.rs` define the quantities.
All values below refer to the original Case-A primary-only evolution. They are
consumed from completed native checkpoints and ledgers, not a replacement solver.

Let f_He=n_He/n_H=0.2454/[4(1-0.2454)]. Element fractions are
x=x_HII, y=x_HeII, z=x_HeIII. The electron abundance per H nucleus is
x_e=x+f_He(y+2z). Charge closure and all five fractions retain their original definitions.
Each cumulative event count is per H nucleus, including helium events.

For the three transitions H I→H II, He I→He II, He II→He III, define
A_i=photo_events_i+CI_events_i-RR_events_i. Dielectronic recombination D returns
He II to He I. Integrating the original stoichiometry gives

    Δx = A_0
    f_He Δ(y+z) = A_1-D
    f_He Δz = A_2
    f_He Δy = A_1-D-A_2
    Δx_e = A_0+A_1-D+A_2.

These identities specify a direct physical interpretation of the event inventory.
The saved numerical residuals are measured and reported. The original state
nuclei/charge tolerance is not silently applied as a new cumulative reaction-ledger
accuracy theorem. The counts are integrated events, not distinct atoms or probabilities;
one nucleus may be ionized and recombine repeatedly.

## Photon inventory

N_gamma is the represented photon stock per H. S_N is the accumulated injected
stock after the selected escape-fraction source. A_N is absorbed photon count and
B_N is lost grid-boundary count. The native initial stock is zero. Therefore

    N_gamma + A_N + B_N - S_N = r_N,
    A_N - sum_i photo_events_i = r_abs.

The boundary ledger covers the actual spectral-boundary accounting of transport
and source deposition. It is not identified with a spatial escape fraction.
The thermal escaped-energy ledger is also distinct from the source f_esc=0.2.

## Energy inventory

The original constants are k_B=1.380649e-16 erg/K,
1 eV=1.602176634e-12 erg, and thresholds
chi=(13.598434599702,24.587389011,54.41776) eV.
Gas thermal energy W=w_erg_per_H/(eV in erg) and ionic binding energy are

    B = chi_H x + f_He[chi_HeI y+(chi_HeI+chi_HeII)z].

The equation of state gives W=(3/2)k_B T[1+f_He+x_e]/(eV in erg).
Writing U_gamma for represented photon energy, E_escape and E_boundary for
the native loss ledgers, W_th and W_gamma for the recorded expansion work,
S_U for injected energy and Q_CMB for signed CMB input, the native invariant is

    W+B+U_gamma+E_escape+E_boundary+W_th+W_gamma-S_U-Q_CMB = E_initial+r_U.

All terms have units eV/H. For a partition of external source plus initial energy,
the CMB term is -Q_CMB; a negative input is a positive cooling loss. Retaining
E_initial prevents a spurious percent-level interpretation of a small residual.
The native original photon/energy acceptance is |r|<=1e-8 max(1,source inventory).
This invariant tests accounting and supplies a source-qualified physical partition;
it does not measure the trajectory's discretization error.

## Resolution and signed geometry response

At a=0.2, compute each inventory at T0 and T1, its D01=T1-T0 in each case,
the signed response Delta_k=PLUS_k-ZERO_k, and D01_pair=Delta_1-Delta_0.
Do not sum terminal cumulative ledgers from multiple continuation segments;
the final checkpoint already includes all earlier accepted events. Intermediate
checkpoints may define cumulative epochs and increments, each counted once.

The background obeys H_q(a)=sqrt(H_F(a)^2+s_q(a)^2),
s_q=q_ref H_F(a_ref)(a_ref/a)^3, dt/dln(a)=1/H_q.
Thus H_PLUS>H_ZERO and a_PLUS(t)>a_ZERO(t) after the same initial slice.
For every represented common proper-time query and any scalar X, write the exact
finite identity

    Delta_t X = X_PLUS(a_PLUS(t))-X_ZERO(a_ZERO(t))
              = [X_PLUS(a_PLUS(t))-X_PLUS(a_ZERO(t))]
                +[X_PLUS(a_ZERO(t))-X_ZERO(a_ZERO(t))].

The first bracket is the clock displacement on the PLUS history; the second is
the fixed-a response at the actual reference a_ZERO(t). This avoids equating a
grid index to the same scale factor. Both PLUS evaluations must be bracketed by
consecutive saved native rows from a retained window. Missing windows are censored,
never filled with extrapolation or interpolated across a sparse unsaved gap.
Linear-in-ln(a) owner interpolation remains primary; local PCHIP only measures
interpolant sensitivity on those same represented windows.

The decomposition may explain opposing signs of two coordinate comparisons.
It neither changes the coordinate convention nor establishes a resolved physical
detection. The original T2 and separated energy/angular refinements still determine
AX11's evolution-resolution obligation. No additional theorem is made a prerequisite.

## Paired ionization milestones

For each actual first upward x_HII crossing at0.1,0.5,0.9, consume its native
lower/upper bracket. Report PLUS-minus-ZERO proper time and redshift separately,
and the corresponding T1-minus-T0 change. Bracket widths measure event localization
on saved output; their overlap is not an evolution-error certificate. This is a
homogeneous ion fraction milestone, not a spatially averaged ionized filling factor.
