# PW19 snapshot on the saved GRID044 geometry

The exact PW19 epoch z*=2.479 lies inside the saved GRID044 interval z∈[2,20]. Its compatible chart location is η*=ln(21/3.479), with a*=1/3.479. The prior donor contract supplies the geometry interpolation representation and a fixed-comoving reference-density law. No source history or new trajectory is needed to define a local counterfactual snapshot. Actual ionic populations and temperature at that location still require the donor data and a justified state reader.

## Inputs actually inspected

PR233 was read at head 833837745c1bfb902f5c09ae00373eaace35038a. Its `runtime_inputs/endpoint/ACTUAL_STATE_BINDING.json`, saved here as `PR233_ENDPOINT_STATE.json`, supplies the actual z=2 endpoint and the reference normalization. Its `runtime_inputs/helpers/donor_projection.py` implements the declared saved geometry reader. The local previous-unit `intake/pr233_DONOR_CONTRACT.json` pins `grid044_history.npz` SHA256 ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b and 201 geometry knots. The binary has not been restored in this lane. PR233 delivery identifies its portable archive, not a fresh run.

The endpoint reference is n_ref,0=0.19078721280843758 m^-3 at a_today=1, S_ref=0, and one present coordinate volume of 1 m^3. This normalization is a bookkeeping count; it is independent of actual hydrogen or baryon changes. Thus the declared compatible density is

    r*=n_ref,0 a*^(-3)=0.19078721280843758 (3.479)^3 m^-3.

This follows the saved reference convention, rather than a fitted physical gas history. The endpoint target vector and temperature are at z=2 and cannot be transplanted to z=2.479. The endpoint's actual He4/Href total is 0.082, whereas REC119's conditional initial inventory uses 0.08112582781456953; these are different model states.

## Constructive geometry and clock map

Use signature (-,+,+,+) and the normal proper-time orthonormal tetrad. The saved reader declares H(η)=exp(PCHIP(η_k,log H_k)), b(η)=Hermite(η_k,b_k−b_0,s_k/H_k), with extrapolation disabled. Define A_perp=exp(η−b), A_parallel=exp(η+2b), V=A_perp^2 A_parallel=exp(3η). These normalized coordinate scales equal one initially. The cosmological scale factor is a=exp(η)/21. Coordinate rescaling between these charts does not insert an extra 21^3 in physical density or the normalized momentum Jacobian.

The expansion tensor is diag(H−s,H−s,H+2s), s=H db/dη, and has trace 3H. A proper-time local residual F transforms as F_η=F/H exactly once. For fixed background and epoch, J_η=J/H. If H is part of the differentiated state, the correct JVP is δF_η=δF/H−F δH/H^2. The PW19 datum supplies no derivative with respect to epoch, so an η/time derivative of its spectrum is an unqualified input, not zero. The local clock may be t*=0; absolute elapsed time is unnecessary for a stationary local callback. A history claim requires the declared integral dt=dη/H and source history.

PW19 bath-rest isotropy can be paired with the donor normal tetrad by explicitly selecting stationary targets and equality of bath and normal four-velocities. This is a physical frame assumption. A tetrad spatial rotation is gauge and leaves scalar rates unchanged; a Lorentz boost changes measured energy, angle and incident distribution and requires a transformed source.

## Reference-to-native-state map

Let x_i=n_i/r be donor abundances per Href, permuted by the actual 21 species labels. Set β=Σ_i A_i x_i, n_b=βr and Y_i=x_i/β. Then A·Y=1 and n_e=n_b q·Y=r q·x. Nuclear charge and electron count therefore agree across the map. If β is fixed by the frozen inventory, δY=δx/β and δn_b=β δr. In a varying inventory, δβ=A·δx, δY=δx/β−x δβ/β² and δn_b=β δr+r δβ; retaining these terms is necessary for a physical JVP. The native API's normalization policy must be fixed before differentiation.

For the selected HeII one-body event, n_HeII=r x_HeII=n_b Y_HeII. Its proper-time number source is Γ n_HeII ν, where ν consumes one HeII, produces one HeIII and one electron. The default per-reference residual is Γ x_HeII ν and the native per-baryon residual is Γ Y_HeII ν. Therefore Γ is independent of the density normalization, while SI volume rates and energy sources require the actual density. For an explicitly evolving reference, use (S_i−x_i S_ref)/r and differentiate S_ref; the present donor has S_ref=0.

In SI the external radiation sink, binding source and primary-electron source obey

    Q_rad=−eV_J n_HeII A,
    Q_bind=+eV_J n_HeII χ Γ,
    Q_primary=+eV_J n_HeII K,
    Q_rad+Q_bind+Q_primary=0,

using A=χΓ+K and eV_J=1.602176634e−19 J/eV. The equality is also satisfied by every fixed-source JVP. K remains primary kinetic energy; thermal heat is unspecified. Positive out-of-grid tails and atomic rates above 50 keV remain in their existing separate ledger.

REC119 explicitly permits ElementalElectronicEquality for He3/He4. Reusing that conditional model assumption is different from deriving isotope-dependent rates from PW19. If the new source binding adopts it, the decision must be explicit and the underlying provider qualification remains elemental. A new isotope claim needs isotope-specific data.

## What can close without an IVP

An actual REC callback snapshot can close its local source/state/normalization/JVP subobligations after (i) selecting or recovering a target state with explicit qualification, (ii) applying the map above, and (iii) evaluating bounded residual/JVP and conservation controls. If a positive frozen control state is selected, it is a controlled callback test, not a reconstructed cosmological state. A physical saved-state claim requires the NPZ target and temperature fields at η*, a declared interpolation rule with relevant accuracy, and donor model identity. Geometry interpolation alone does not supply ionic-state interpolation.

The original REI-EXP-SCENARIO gate additionally requires the 21-label coverage map, source/absorber/owner/reservoir matrix, chosen event set, domain, initial/boundary data and named observable. It may admit one explicitly qualified instantaneous scenario; this note alone does not complete that gate. The current usable observable is a local reaction-rate/source diagnostic. Optical depth or a spectrum requires the missing history and observation operator.

V6 remains OPEN_INPUT: the fresh intake found no new actual native full33/reduced30 derivative client or current owner receipt. Its exact affine map F_red=R F_full(b+Lz), J_red=R J_full L can be checked at a frozen state without an IVP once that client exists. This local REC119 derivative work is not automatically the V6 native-client gate. REC-HISTORY retains its source-matched reference/derivative obligations. REI-L4 retains live gas/radiation/geometry feedback, full/reduced and refinement requirements; no snapshot closes them.

Symmetry/gauge, invariant and observable roles remain separate: tetrad covariance is a representation property; charge/nuclei/energy identities constrain the source; Γ, K and local SI residuals are snapshot diagnostics; light-cone observations require histories. No new no-go theorem, numerical execution, source extrapolation, producer mutation, or budget debit is claimed in this research lane. Global DAG remains 30/88.
