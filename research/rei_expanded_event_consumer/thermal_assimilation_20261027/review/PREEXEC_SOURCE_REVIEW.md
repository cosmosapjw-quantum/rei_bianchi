# Independent preexecution source/scientific review

Date: 2026-10-27 UTC  
Reviewer: supplier_intake, inherited GPT-6 Astra Pro  
Decision: **PASS_SCOPED_FOR_FROZEN_IMPLEMENTATION**  
Current-task blocking findings: **0**  
Targeted corrections required: **0**

This is an independent read-only review of the root-frozen conditional model and its actual supplier interfaces. The reviewer recovered/read supplier inputs but did not author the thermal-join derivation, choose the model, implement the new assembly, or run its checks. It is not a second numerical admission or an independent empirical validation of the native fits.

## Reviewed identity and transition

- Working branch observed again by GitHub ref GET: research/rei-thermal-assimilation-20261027 at **8057f121d7ba6adc4abebd96b06ed3ab2c38092f**, matching the root freeze.
- ROOT_FROZEN_CONTRACT.md: SHA256 **d6db25daef4c89be9c85c268a5d21cb9aa8a3f34548068f2e76ee95bcd7019b3**, 8,031 bytes.
- THERMAL_JOIN_DERIVATION.md: SHA256 **ad8f2ca6b77da92b229aae8bc18906ce264989700aeb9d077005938f839ab480**, 17,070 bytes.
- Current AGENTS_WORKING.md was read; its computed Git blob **6464cd96b7023e3e91e30246bc93650d4e435a10** matches the root-stated policy identity.
- Read the theory author's clearly labelled R6_PREFLIGHT_REVIEW.md, the R1 publication ACK and exact VENDOR_MANIFEST.json. The live collaboration inventory showed the theory worker completed and the distinct mechanical implementation worker active.
- The root freeze reports that R1 Drive/Dropbox ACKs and parallel returns were checked. This review does not relabel that root observation as a new independent cloud readback or upload.

**PASS → next action:** continue the frozen implementation. Root's separate scientific GO still follows the specified preimplementation package ACK and source/checker identity recording. Then run only the authorized new bounded checker and return code/raw outcomes for independent review. No additional theory search, old-suite replay, or new governance gate is required by this review.

## Actual source routines inspected

1. Native REC119 atomic_network.py, especially rates() and evaluate(): Grr/Gdr act on column Y and have units m³/s; inherited evaluate() uses total-charge ne=nb*qY and therefore its RR/DR side outputs must not supply this changed thermal assembly.
2. Unchanged REC124 thermal_sources.py::ThermalSources.coefficients(), recombination_moments.py::RecombinationMoments.evaluate(), the source-lock meanings and existing closure distinction.
3. Unchanged REC124 compton_budget.py::planck_reference_power() and its actual constants.
4. Unchanged HE exchange_closure.py::monatomic_caloric() and temperature_rhs().
5. The root freeze and full join derivation, including their value, tangent, normalization, domain and scoped-claim equations.

Exact supplier refs remain REC124 **e6ecef7624e39bee66b39e09d99fe355f76e2eae** and HE **ac6042a6b0610b09d0576538767ee0299389a5eb**. Prior recovery byte identities and the root vendor-copy receipt are reused, not promoted to a claim that numerical outputs must be byte-identical.

## Scientific assessment

### One thermal electron pool

The definitions g=q·Y−zeta, chi=(1+q)·Y−zeta and ne_th=nb*g are used consistently in RR, DR, Compton and the caloric count. With R=R_RR+R_DR, j=nu*zeta and h=nu*w,

- ion source is nb*(P+R);
- fast number source is nb*(q·P−j);
- thermal electron source is nb*(q·R+j);
- total free-electron source is therefore nb*q·(P+R), counted once.

Because native photo/RR/DR preserve ion count, the thermal particle source is nb*(q·R+j). It contains no duplicate photoelectron birth. The frozen exclusion of whole ThermalSources.evaluate() and inherited photo-helper RR/DR side outputs is necessary and sufficient at this interface level.

The HE monatomic rows give Cv=(3/2)kB*nb*chi and count power=(3/2)kB*T*nb*(q·R+j). Passing centered power nb*(h+qC−L), with zero expansion/shear/divergence for this isolated source increment, yields exactly the frozen log-temperature row. The imposed source-only setting does not claim that cosmological expansion is absent from the full model.

### Binding, thermal, fast and radiation ownership

Let I be the native cumulative ionization-energy vector in joules. The frozen escape definition Eesc_s=L_s−I·R_s has the right sign and agrees with the native separation of binding release and kinetic cooling. The sum of ion, fast, thermal and external-ledger energy derivatives cancels once:

| Selected process | Binding change | Fast kinetic change | Thermal kinetic change | Signed external radiation change |
|---|---:|---:|---:|---:|
| Photoionization | I·P | +k_gamma | 0 | −a_gamma |
| Thermal RR/DR | I·R | 0 | −L | +L−I·R |
| Declared assimilation | 0 | −h | +h | 0 |
| Selected Compton | 0 | 0 | +qC | −qC |

The existing photo identity is I·P+k_gamma−a_gamma=0. Binding remains derived from Y, and the single w_ext row aggregates named external/escaped contributions; no duplicate evolved escape reservoir is introduced. RR/DR radiation is not also deposited as thermal heat.

The caloric term −j/chi is essential. Its presence correctly permits bath cooling when an entering electron carries less energy than the bath mean translational energy. It does not require a fabricated negative heat input.

### Actual source and thermal coefficient domains

The selected source remains PW19 He II at z=2.479, threshold54.42 eV, photon54.42..50000 eV and primary0..49945.58 eV. Conditional electronic equality of He3/He4 is inherited; no H1/CR-low-energy substitution is made. The constructed zeta,w fixture is explicitly a manufactured fast population on the real saved background, not a recovered cosmic history.

The actual T=14919.863839279506 K and frozen small trial variations lie within the native100..10^6 K coefficient domain. Neutron/tritium coordinates0,5,6 and corresponding trial entries remain zero, and the assembly selects photo+RR/DR rather than the native decay matrix. Signed DR summands, total positivity, structurally absent channels and present-but-underflowed channels keep their original meanings.

The root correctly confines T=T_rad≈9.48 K to the Compton helper alone. Evaluating the joint REC/Mao system there would be outside its domain, but that operation is explicitly excluded.

The RR Mao-factor × parent-rate hybrid and native conditional DR energy-moment closure retain their original scientific ceilings. This join does not independently calibrate their physical accuracy.

### Compton and analytic tangents

The native Planck helper constructs its own blackbody U_rad and gives Q_C=4*K_C*ne*kB*U_rad*(T_rad−T). Dividing by nb and the same thermal caloric count gives the stated qC and g*B_C/chi. The nonthermal electrons do not enter this thermal Thomson/Planck closure.

For tau=T_rad/T and a_d=da/a, the displayed derivative
dB_C=−(8K_C/3)*U_rad*((5*tau−4)*a_d+tau*dell)
follows directly from T_rad∝a⁻¹ and U_rad∝a⁻⁴. The density and temperature product terms in dqC are present. There is no inferred UV Compton term from unrelated PW19 absorption moments.

The RR/DR tangents include both dne=dn_b*g+nb*(q·dY−dzeta) and the native coefficient logT derivatives. They do not divide by g or q·Y and remain regular at g=0.

### Mixed coordinates, changing reference and clock

The first24 rows have density-like normalization, whereas the logT row does not. Multiplication by beta/nb only on those24 rows and division of all25 rows by H are correct. The corresponding product and clock quotient terms are explicitly present.

The reference input transformations for Y, zeta, w and signed w_ext are all required and are included. The chosen isotope-preserving native direction has A·v=0; constructing dx=beta*v+Y*dbeta then gives A·dx=dbeta. The frozen dbeta/beta=.07, dr/r=−.06 and dnb/nb=.01 obey dnb=r*dbeta+beta*dr. The scale-factor variation da/a=.02 is consistent with dr/r=−3*da/a at fixed r0.

The general physical-reference control Fx=(S−x*Rr)/r and its stated derivative are algebraically consistent. It is explicitly labelled a source/reference control, with no −logT*Rr/r term and no inferred fast-energy pressure work or radiation-redshift evolution.

The value nu*=H* is only numerical equality at the selected snapshot. Independent dnu and dH are allowed by the declared parameter convention and do not contradict it.

### Scope and controls

The operator dmu/dt=−nu*mu with energy-independent nu gives j=nu*zeta and h=nu*w for every finite positive energy measure. That exact moment statement is valid without reconstructing a spectrum. It is a conditional selected closure, with physical-rate uncertainty/admission left null. The two-measure example correctly limits an alternative energy-dependent closure; it is not a universal no-go statement.

The predeclared mixed direction, two allowed FD steps, fixed operand-based row scales, structural-zero treatment and unchanged tolerances are adequate for the stated changed-assembly directional check. Their success would establish that finite check only, not a full Jacobian certificate, whole time-state tube, continuous convergence or calibrated stopping law.

No current-task scientific correction is required before the frozen implementation.

## Limits, costs and completion

This review ran **no provider imports, coefficient evaluations, symbolic commands, test suites, finite differences, quadratures, IVPs or NCP work**. It read source/documents, checked the remote ref and recorded document identities. Read-only review CPU/wall were not instrumented and remain **UNKNOWN_NOT_ZERO / null**.

Original working completion remains **32/88**, central **27/88**; this review adds **0** original completed nodes. Full REC-COUPLED/REC-EXP-COUPLED, physical stopping admission, native integration/V7/V8 and L4 keep their existing separate gates. No unchanged gate has been reopened and no inherited budget has been reset.

