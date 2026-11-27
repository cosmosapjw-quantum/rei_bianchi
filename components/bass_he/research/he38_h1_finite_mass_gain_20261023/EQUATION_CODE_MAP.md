# Equation–data–code map

| Theory relation | Component/API | Units / numerical decision |
|---|---|---|
| μ=mζ; moments_μ=moments_m/√ζ | h1_finite_mass/model.py, FiniteMassModel.evaluate | Byte-preserved HE37 provider; new finite-mass identity |
| Eq2–6 Jacobi velocities and invariants | event_kinematics | SI; fixed physical mass or labelled artificial kinematic control |
| Eq12 barΥ; Eq14 Λ,U1 | transfer_mean_eV; evaluate.sharing_moment / first_jacobi_energy_moment | log1p near threshold; no added production quadrature |
| Eq18 three species heat | evaluate.heat_per_pair_J_m3_s | Stable closed forms; multiply n_e n_H |
| Eq19 small heavy combined heat | evaluate.heavy_heat_per_pair_J_m3_s | Direct expression, not Q_H+Q_p subtraction |
| Eq23–24 three-by-two response | evaluate.stf_coefficients_m3_s; finite_mass_source | Column0×n_Hπ_e, column1×n_eπ_H |
| Eq25 total STF | finite_mass_source.total_J_Pa_s | Direct contraction preserves tinySTF |
| Q_total=−Ir; S=J+2QId/3 | finite_mass_source and h1_ci_source | One heat owner; separate direct total |
| Pure-H ne=nB Yp; number source | bridge.h1_ci_source | Physical versus frozen-ne donor Jacobians labelled |
| Eq20 reaction dotT | bridge.h1_ci_source | Explicit all-retained thermal census only |

Donor file hashes and source licensing/provenance are in components/finite_mass/DONOR_PROVENANCE.json. Exact new theory checks live in theory/CHECKS.json; independent nonauthor review and raw numerical controls remain separate evidence.
