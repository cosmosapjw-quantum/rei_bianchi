# Independent derivation: joint photon–target collision and reference normalization

Reviewer: `/root/collision_review`, separate from the theory and implementation authors. This document is an independent analytic derivation. No new scientific numerical execution or old-suite replay was performed by this reviewer. The preceding opacity response is accepted at its recorded finite scope and reused.

## Scope and dimensions

At a fixed proper time in the normal tetrad, let N_j=n_gamma,j/n_ref be a finite packet count per reference particle and y_i=n_i/n_ref the 21 target populations in the requested label order. E_j is the normal-observer packet energy in eV, sigma_aj is the inherited valence cross section in m², n_ref>0 is m⁻³, and c=299792458 m/s. Each adjacent charge edge e has lower state l(e), upper state u(e), threshold chi_e and an elemental cross-section row a(e). S_ie=delta_i,u−delta_i,l is its incidence column. Electronic isotope equality is the inherited model assumption.

Define k_ej=c n_ref sigma_a(e),j [s⁻¹] and r_ej=y_l(e) k_ej N_j [events/(reference s)]. At a frozen instant these are bilinear collision events. The joint number RHS is

    F_Nj = q_j − sum_e r_ej,
    F_yi = sum_e,j S_ie r_ej.

The normalized photon source q_j has photons/(reference s). It already includes whatever quadrature/escape/source normalization its producer specifies. It must not receive a second angular factor or escape factor. The finite packet fixture must identify whether its packet counts are actual recovered donor cells, constructed from the previous source model, or synthetic test values. A small packet test is not a quadrature-convergence certificate for the earlier continuous radiation response.

## Full collision crossblocks

At fixed n_ref, E and q,

    dF_Nj/dN_k = −delta_jk sum_e k_ej y_l(e),
    dF_Nj/dy_i = −sum_e delta_i,l(e) k_ej N_j,
    dF_yi/dN_j = sum_e S_ie k_ej y_l(e),
    dF_yi/dy_k = sum_e,j S_ie delta_k,l(e) k_ej N_j.

The photon-to-target and target-to-photon blocks are both essential. The previous frozen-radiation target/source Jacobian provides only a subblock and cannot replace them. An external source with fixed templates q_j=sum_s alpha_s q_sj adds dF_Nj/dalpha_s=q_sj. If the template parameters change the photon inventory as an independent state, their dependence must be specified; independent state and source parameter coordinates should not be conflated.

Electron number is derived from ionic charge, y_e=q_ion^T y. It is not an extra independently evolving chemistry variable. Every photo edge increases ionic charge by one, so its physical electron-production rate is sum_e,j r_ej.

## Single-event energy ownership

Use neutral-ground reference epsilon_i equal to cumulative ionization thresholds. Then epsilon^T S_e=chi_e. A primary-electron injection tally K obeys

    F_K = sum_e,j (E_j−chi_e) r_ej.

This K is an energy-injection ledger, not a common-temperature thermal energy or a solved secondary-electron distribution. Photoionization absorbs E_j, stores chi_e in the ionic state and injects E_j−chi_e into the primary electron. Consequently

    sum_j E_j F_Nj + epsilon^T F_y + F_K = sum_j E_j q_j.

Binding energy B=epsilon^T y may be derived algebraically. If implemented as an additional ledger coordinate, its initial consistency B=epsilon^T y and the corresponding derivative identity must be checked; do not count both B and epsilon^T y in the same total-energy sum. An external-injection energy tally can satisfy F_ext=sum E q, leading to zero collision-plus-source residual after subtracting it once.

For characteristic packets E_j=E_j(t), the derivative of photon energy is E^T dot N + dot E^T N. The latter is redshift work, not collision loss or primary-electron heating. The fixed-geometry collision Jacobian is a full Jacobian of the selected collision state, not the entire evolving photon-energy/temperature/nuclear system.

## Normalization and quotient terms

A physical number density n_i satisfies dot n_i+3H n_i=C_i. For a chosen positive reference density n_ref define

    Lambda = (dot n_ref + 3H n_ref)/n_ref.

Then z_i=n_i/n_ref obeys dot z_i=C_i/n_ref−Lambda z_i. The original conserved-comoving Href convention has Lambda=0 even though nHref itself changes as a⁻³. A physically produced reference species generally has Lambda≠0; calling nHref time dependent alone is not a reason to insert an extra3H.

For externally prescribed n_ref(t), Lambda(t), and reference-normalized source q, the full normalized state z obeys

    F(z)=F_collision(z)+Q−Lambda z,
    J=dF_collision/dz−Lambda I.

If Lambda depends on the state, the additional term −z (grad Lambda)^T is required. If n_ref itself depends on state, the factor k=c n_ref sigma contributes (F_collision/n_ref)(grad n_ref)^T as well. Source normalization q=C_source/n_ref has its own derivative when physical source and n_ref vary. The implementation must explicitly state which inputs are independent and which gradients are supplied. A supplied instantaneous Lambda and gradient cannot by itself certify that a complete physical reference-density history has been admitted.

For a smooth reference rescaling n_ref,2=f n_ref,1, z_2=z_1/f, q_2=q_1/f, and Lambda_2=Lambda_1+dot f/f. Because collision densities are bilinear, F_collision,2=F_collision,1/f when n_ref,2=f n_ref,1. Hence F_2=F_1/f−(dot f/f) z_2. This is a useful independent coordinate-equivalence check. A constant f reduces to F_2=F_1/f.

The invariant statements become

    dot(sum_isotope y) = −Lambda sum_isotope y,
    charge^T F_y = electron_production −Lambda y_e,
    E^T F_N + epsilon^T F_y + F_K
        = E^T q −Lambda(E^T N + epsilon^T y + K),

with extra dot E^T N if total photon-energy evolution is included. Physical proper-volume identities are recovered by multiplying by n_ref and using its derivative. A derivative test must distinguish the collision electron-production ledger from the total derivative of normalized y_e when Lambda≠0.

## Positivity, selected scope and gates

At a zero photon coordinate N_j=0, its collision loss vanishes and a nonnegative external q_j gives nonnegative inflow. At y_i=0, the outgoing photo event vanishes and incoming adjacent events remain nonnegative. The −Lambda z term also vanishes on that coordinate face. This is a local tangent-cone property of the ODE; it does not certify positivity of an arbitrary finite time integrator. No new IVP is needed for this node.

The photon diagonal block is dissipative, the target charge block has nonnegative off-diagonals and zero isotope-column sums before normalization. Crossblock signs have a physical depletion/production pattern and need not make the entire joint Jacobian Metzler. Source-off with positive photons still has collisions; zero-radiation with nonzero injection still has source creation. Tests must distinguish these cases.

Three axes remain separate: (1) LRS/reflection and coordinate rescaling at fixed physical observer; (2) isotope, charge, event and energy-transfer identities, with quotient corrections where appropriate; (3) normal-observer packet absorption and target/energy production rates. Physical n/T sources, neutron-decay proton feed, CR/neutrino channels, LiI core/Auger and thermal deposition are still separate open inputs. Main N6 HOLD and NO_MORE_IVPs remain unchanged. The construction is not a new no-go theorem.

Before execution require an exact selected state vector, fixed packet/source provenance, declared n_ref/Lambda dependence, frozen analytic Jacobian and independent finite-difference or complex-step gates, exact source/provider/input bindings, invalid-domain checks, source-off/zero-radiation distinctions, differential energy and isotope/charge checks, reference-equivalence checks, and one bounded child charged to the existing campaign. New science remains NOT_RUN until that actual child returns.
