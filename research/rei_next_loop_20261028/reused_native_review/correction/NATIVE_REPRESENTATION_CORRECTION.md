# Source-temperature representation correction from the native R6/C9 review

Unit: finite_thermal_endpoint_20261028. Reviewed source pin: b77c7b8d45c48a7e4722e733309430d5ba668b0d.
Finding: F1 in the preserved native provisional and post-disclosure reports.
This additive correction governs the represented-input interpretation of section 4 of review/R6_SOURCE_BATH_RECONCILIATION_20261028.md at that pin. The original historical text remains preserved.

## Corrected claim

Let theta_a be the independently represented source energy-temperature value in eV, T_native the independently represented positive native temperature in K, k_src the represented source Boltzmann constant in eV/K, and EV_src the represented source conversion in J/eV. Keep k_B_SI = 1.380649e-23 J/K. Define

    T_a^E = theta_a * EV_src / k_B_SI
    delta_theta = theta_a - k_src * T_native.

For these represented inputs, the exact relation is

    T_a^E / T_native
      = k_src * EV_src / k_B_SI
        + delta_theta * EV_src / (k_B_SI * T_native).

Equivalently,

    T_a^E - T_native
      = (k_src * EV_src / k_B_SI - 1) * T_native
        + delta_theta * EV_src / k_B_SI.

The constant-factor-only formula applies to an unrounded defining relation theta_a = k_src*T_native, or to represented values for which that product identity is separately established. A binary64 multiplication followed by separate exact lifting of its operands and rounded result does not imply that identity.

## Proof and counterexample

Substitute theta_a = k_src*T_native + delta_theta into the defining expression for T_a^E and divide by positive T_native. The second identity follows by subtracting T_native. Both terms in the temperature difference have units K; delta_theta has units eV.

For a representation-only counterexample, the exact lift of binary64 0.1 is 3602879701896397/2^55. Multiplying it exactly by 3 gives 10808639105689191/2^55. The binary64 source product 0.30000000000000004 instead lifts to 10808639105689192/2^55. Its product residual is therefore 2^-55. This example concerns represented arithmetic.

The original C7 saved bridge contains the actual source residual

    delta_theta = -393372660608921 / 40564819207303340847894502572032 eV,

which is nonzero. This identifies the affected claim for the frozen source as well as for the counterexample.

## Implementation and scope

finite_thermal.py already returns theta_minus_kBoltz_native_eV and computes energy_temperature_K from the independently supplied theta_eV. Its mathematical module and the original source inputs require no change. The finite caloric map, residual transport, JVP, interval bounds, and reference-volume composition retain their stated domains and formulas.

The correction is one source-representation statement. It does not reinterpret a saved algebraic residual as physical uncertainty. Actual REI recipient temperature, native25 and physical radii remain null; full_state_update and L4_ready remain false; global_physical_completion remains null.

The native review's historical He-branch coverage limitation remains explicit: the declared inert-He producer model is supported directly, while the earlier native history/header argument was not independently reconstructed. It is outside the present source-caloric claim.

## Targeted verification contract

One new bounded exact-arithmetic check shall compare the corrected ratio and difference identities with the preserved C7 bridge and original literal packet, using an independent Fraction calculation and the representation counterexample above. It shall not import or execute the source consumer, provider, prior fixture suite, C8 studies, CAS, or any IVP. The initial and post-disclosure native reports remain unchanged. The verification's original source, stdout/stderr, result, and measured complete-command resource record are preserved separately.

