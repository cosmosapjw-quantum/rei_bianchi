# B5C2 results and release scope

Eight new two-state electronic points were continued from R=.5 to .125 a0, followed
by five independent radial-and-angular variational endpoint cases. No new root failure
or hidden amendment occurred. At .125: El=-4.371219290245747 Eh,
Eu=-1.1296940703574545 Eh, |d|=.26123180153209213 a0, F=3.0991246341309613.
The dipole differs from its united-atom limit by +5.2031167%; F by -1.9417596%.
This finite radius is not an approved physical matching radius.

Across the five independent discretizations the maximum differences were
4.799716180059477e-12 Eh in energy,1.6775469902086115e-13 a0 in dipole,
and1.568927797338591e-7 in normalized field distance. These are comparisons
between approximate states, not errors relative to a certified exact state.

The new full suite has59 unique tests;51 were observed failing before their fixes,
and8 are followup or existing-guard checks. The public scalar-kernel slice includes
44 of these tests. Separate wheel installation passed all59. Fifteen independent
80-digit Coulomb oracles gave maximum relative differences1.6111160359567919e-16
for log derivatives and5.1568295922949026e-14 for accumulated inner absorption.
Three DOP853 continuation tests checked matching including the inner absorption.
These are manufactured-operator checks, not physical cross-section calculations.

An extreme-input range review found two nuclear-scale division failures and one
amplitude-overflow failure; the actual failures were preserved and converted into
explicit NumericalFailure without changing physical values or tolerances.

The final archive validation owns ZIP replay results. No old scientific suite was
rerun for backup. No new Fortran/OpenMPI, host optimization, physical scattering,
thermal rate, photon-spectrum or heating calculation was performed.
scientific_PROMOTE=HOLD; EOR_THEORY_GATE=NOT_SATISFIED; Eq55=NOT_RUN;
physical source admission=false; independent scientific review=NOT_RUN.

Next bounded research: EOR_B5C3_INNER_OPTICAL_REMAINDER_AND_BOUNDARY_SENSITIVITY.
Actual inner electronic remainders and their matching influence remain open.
No NCP64 execution is required now; the workstream remains atomic-data-only.
