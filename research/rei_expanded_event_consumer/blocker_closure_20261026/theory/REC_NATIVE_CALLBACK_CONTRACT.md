# Actual REC callback consuming admitted PW19 HeII

Version1.0,2026-10-26. Theory authority next_source_theory; requested Astra role, observed model unexposed. Root owns resources, execution GO and admission. Baseline30/88 at PR236 head6c1604744fbc256a484513f7215dcb39660e6cff. No execution permission follows from this document.

## R1-R4: exact target and inputs

Call the existing native REC21-state RHS/Jacobian with its photo provider replaced exclusively by admitted PW19z2.479 HeII coefficients. Native `AtomicNetwork.rates` and `AtomicNetwork.evaluate` must run unchanged. This is a proper-time local callback, not a trajectory or thez~1100 HyRec departure system.

Native repository cosmosapjw-quantum/rec_bianchi, commitad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7, prefixresearch/rec_rei_hheli_sandbox_20261021. Restored asintake/rec119/:

- code/atomic_network.py: Gitblobe3a0603176304f64b953c0b2faf898d6b75eceb5, SHA256baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80.
- data/atomic_model.json, data/atomic_coefficients.json, provenance/atomic_sources.json and all10 manifest-verified inputs. Intake has restored and byte-verified them. Keep `_verified_inputs()` unchanged.

Actual source: ../lumina_resume_20261026/implementation/run01/MOMENTS.json, SHA2564856cabb34ee24d3c626b795cb1098b228e752c857dda1dc874fe4583deb936e. Reuse its admitted3bands[54.42,204.42],[204.42,2000],[2000,50000]eV, source identity, uncertainty and tail ledgers; no quadrature rerun. Full finite-domain coefficients are Gamma7.130091128981093e-15s^-1, K1.4238389467477924e-13eV/s/target, A5.304034539139303e-13eV/s/target.

The source is an instantaneous isotropic prescribed bath at exactz2.479. Native evaluate has no redshift argument; adapter rejects other sourcez. No redshift/time extrapolation or cosmological state is inferred.

## Species and exclusive source policy

Y_i=n_i/n_b, ordered21labels from native model; n_e=n_b*q.Y, with no additional electron abundance. Selected channels: He3IIindex8->He3IIIindex9; He4IIindex11->He4IIIindex12. Native model explicitly enables ElementalElectronicEquality forHe3/He4. Reuse only this disclosed conditional approximation; preserve distinct nuclearA and abundances. Elemental data are not isotope-calibrated rates. Native thresholds must equal sourcechi54.42eV; reject mapping without explicit inherited equality policy.

All other photo routes are deselected, exactlyzero by route selection rather than a physical zero cross-section claim. Native RR/DR/decay remain unchanged; n/T control inventories remainzero. Native Lyalpha/LINE02 modules are not called, changed or duplicated. No primary energy is sent to gas heat.

## R5: actual native equations and tangent

LetG be native upward transition matrix from outgoingGamma at8/11 only;R=Grr+Gdr;D=native decay;lambda>=0source amplitude. In proper seconds:

    F=lambda*G*Y+D*Y+nb*(q.Y)*R*Y
    J=lambda*G+D+ne*R+nb*(R*Y)*q^T
    deltaF=J*v+(q.Y)*(R*Y)*dnb+(G*Y)*dlambda
    deltane=nb*q.v+(q.Y)*dnb.

T is fixed in these tangents. Preserve the native electron-feedback outer product. The source-on/off difference islambda*G*Y. LetS=Y8+Y11 andepsilon_J=1.602176634e-19J/eV. Photo electron supply=nb*lambda*Gamma*S; binding power=nb*lambda*chi*Gamma*epsilon_J*S; primary power=nb*lambda*K*epsilon_J*S; external-radiation debit=-nb*lambda*A*epsilon_J*S. Return these perband and summed. Baryons/isotope nuclei are conserved, q.G counts one electron/event, binding+primary+radiation sums tozero. These are selected-photo energy partners, not closure of all native RR/DR/decay energies.

For the donor normalization beta=A.x, Y=x/beta andnb=beta*r, direct substitution gives beta*F=(lambda*G+D)x+r(q.x)R*x. Its tangent with fixedlambda is (lambda*G+D)dx+dr*(q.x)Rx+r*(q.dx)Rx+r*(q.x)Rdx. This equalsdbeta*F+beta*dF after the projective state/density tangent map, so no hiddenbeta orreference-density factor enters the native nonlinear recombination term. A new independent remote Wolfram arbitrary2x2 symbolic check returnedzero for the reaction identity, nativeJVP chainrule and per-reference tangent; `NORMALIZED_REACTION_CHECK.json` preserves it. RemoteCPU isUNKNOWN, notzero; this is algebraic evidence, not a numerical source or history result.

For any coefficientC, delta(C*nb*lambda*S)=C*(nb*lambda*(v8+v11)+lambda*S*dnb+nb*S*dlambda). The primary reservoir is nonthermal. External debit accounts an open prescribed bath and is not evolved radiation backreaction. No eta conversion in this callback; a future eta caller must useF/H anddeltaF/H-F*dH/H^2 exactlyonce.

## Concrete native implementation

CreatePW19HeIINetwork(AtomicNetwork) underimplementation/. Override ONLY `_prepare_spectrum`; inherited rates/evaluate remain unchanged. Consume cached admitted moments and initialize:

- `_photo_s`:Gamma at8/11 only; `_Gphoto` via actual native `_transition_matrix(...,upward=True)`.
- `_absorbed_W`:A*epsilon_J at8/11; `_primary_W`:K*epsilon_J at8/11. `_core_W`,`_li1s_photo_s`,`_inner_absorbed_W`:zeroarrays.
- `photon_flux_bins_base`:1e4*Phi per3bands,m^-2s^-1. `photon_energy_eV`:Psi/Phi perband, ONLY for exact energy-density diagnostic sum(Phi*Emean)*epsilon_J/c; never evaluate cross-sections or inject a delta spectrum at these means. Expose original spectral grid/provenance and bandedges separately.
- Use native read-only helper for arrays. Reject any cutoff argument rather than silently truncate. Require explicit source route/isotope policy/unique owner; duplicate photo owners reject.

Native photo_cross_sections remains restricted<=200eV and is never invoked for the new domain. C23B owns the admitted54.42..50000eV external fit; a rate-provider insertion does not extend the native cross-section routine. Original model input stays unchanged; selected external route metadata supersedes its historical photon_field for this object only.

Full electron support extends49945.58eV. Full-source150eV kinetic injection rejects; low submeasure keeps explicit positive tail. Above50000eV atomic absorption remainsunknown from saved sourceledger, notzero. No clipping/renormalization/heating fraction.

Detailed balance: selected one-way external photoionization plus existing case-A escaping recombination is a driven open model. No LTE/equilibrium identity is asserted for independent fits. A closed reciprocal bound-free/free-bound pair would require state-resolved/Milne source evidence; this adapter does not alter native reciprocal or line equations to force it.

## Matched finite snapshot and bounded acceptance

Primary output uses the actual restored GRID044 donor `intake/donor/event_consumer_20261026/runtime_inputs/endpoint/grid044_history.npz`, SHA256ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b. Apply geometry agent's finite snapshot binding: eta*=ln(21/3.479), unique adjacent donor eta knots, theta=(eta*-eta_k)/(eta_{k+1}-eta_k). Interpolate `atomic_abundance_per_Href` and `temperature_K` by convex linear interpolation in eta, never scaled coordinates. Permute by exact atomic-state labels toREC21 order; beta=A.x, Y=x/beta, nb=beta*r with the preserved reference-density law r=n_ref0*(3.479)^3. The native initial inventory is not substituted: GRID044He4/Href0.082 differs from nativeHe4/H10.08112582781456953. Native constructor initial_Y is unused for main evaluation.

This newly declared finite representation preserves positivity and linearly interpolates each isotope total; no continuum interpolation accuracy is asserted. Record both bracketing rows,theta,minimum population,beta,T,nb and sourcez. Continuum/state interpolation uncertainty remainsnull. Use exact native H/b reader only if geometry diagnostics requested; no source-time derivative or IVP. A labelled native-inventory control withHe fractions(.2,.5,.3),T10000K,nb1 remains available only as a secondary arithmetic fixture if specifically needed, not as the main source-consumed state or a mandatory extra run.

One newly authorized execution, noIVP or oldsuite replay:

1. Verify inherited native methods unchanged, exact21labels/A/q, explicit policy/threshold and sourceidentity. Species authority decidesREC-EXP-SPECIES separately.
2. Atlambda0/1 native source difference=GY; RR/DR/decay unchanged. Otherphoto routes exactlyzero. Perband energies match cached source.
3. Selected source baryon/isotope/charge/energy and SI number/energy-density diagnostics: scaled residual<=2e-14 using positive event/power scales, nevermax(1,tinyquantity).
4. Full nativeJVP at the matched finite snapshot: two directions(a)v8=-.1He3total,v9=+.1He3total,v11=-.1He4total,v12=+.1He4total;(b)v1=-1e-5,v2=+1e-5; allotherentrieszero. Centered differenceh1e-4, compare fullvector toJv withscale=maxabs(referenceJVP), tolerance2e-8. In direction(b) Gv=0 exactly, so use the sum of returned native rr_rhs+dr_rhs+decay_rhs in the finite difference to avoid subtracting two large unchangedphoto contributions; the reference remains the full nativeJv. This is algebraically the same full directional derivative and changes no tolerance. Do not replay21columns. This checks electron-mediated native recombination response.
5. Lambda andnb tangents samecentralh, tolerance2e-8; direct analytic source-energy tangent identities2e-14. Atlambda0 photo vanishes exactly and derivativefinite.
6. Reject wrongsourcez, missingisotopepolicy, duplicateowner, cutoff andfull150eV injection. Preserve native negative-density andshape guards. Native signed NewtontrialY remains allowed, no clipping; thiscontrol itself is positive.

FD2e-8 is a new adapter differential tolerance, not physical accuracy: nativeF is quadratic inY, so centered directional truncation vanishes algebraically atfixedcoefficients; residual is floating cancellation proportional toeps/h andconditioning. Record observed discrepancy; do not loosen onfailure. Existing scientific/physical tolerances stay unchanged.

Output actual nativeRHS/Jac/JVP, sourceon/off difference, event/energyledger, sourceidentity andunknown provider/model/isotope/interpolation uncertainties. Gascontrol must be labelled. Root freezes command/limits/byteidentity/cumulativeaccounting/GO; failedraw output is preserved, noautomaticretry.

## R6-R10 and original gates

Fresh independent authority reviews changedadapter, unchangednative methodidentity andactualraw output. ScopedPASS can supportREC-EXP-SPECTRAL only when itsREC-EXP-SPECIES dependency is admitted. Original gate:units+applicableDB+energypartner+bandinterfaces+exclusive nativeLyalpha; pass_next=actualsource residual/JVP toREC-FIELD. This is actual native consumption, not a detachedtoy.

REC-FIELD separates ownerexclusive energyexchange and model-calibration evidence from floating conservation. This callback supplies a genuine native abundance residual/JVP with an explicitlyopen photonreservoir; source/model uncertainty remainsunknown. ItsREC-LINE02 dependency is conditional on selected_spectral_channel_is_native_Lyalpha, which thisHeIIcontinuum route does not activate. Judge the original selected source/band ownership, particle/heat/binding/nuclear separation and uncertainty criteria; do not add a mandatory live photon-backreaction requirement. The explicit debit remains an open-reservoir term and is not described as evolved backreaction.

REC-H6-TRACE staysopen: a single-z spectrum supplies no actual retardedBianchi trace, causalprefix/fixedstencil or nativedeparture-reference derivative. Do not map it into oldz~1100 hydrogenhistory. This missinginput does not block the newproper-timecallback.

Axes: isotropic bath-rest tetrad/passive-rotation-invariant scalar rates; isotope/baryon/charge and selectedenergy invariants; actualsource-driven nativeelectron/abundance response at explicitcontrol. No tau/history/CMBprediction, newnuclear physics orstrongno-go claim.
