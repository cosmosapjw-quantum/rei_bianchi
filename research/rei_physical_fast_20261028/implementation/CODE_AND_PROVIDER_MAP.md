# Physical-source adapter: C2 map

The additive current default is ON_refined. It resolves to the already completed
saved case without importing its solver. ON_base and ON_refined share all source
and escape settings; their only differences are rtol/scaled-atol. Explicit case
selection remains available. Completed source files and trajectories are inputs,
not mutation targets.

The usersupplied `physmath-research-loop` canonical package was read at
`skill://user/6aa0657100b08191b7d67482d1f97c1d/physmath-research-loop/SKILL.md`:
it declares intrinsic protocol1.0.0. CODING_LOOP, RESEARCH_POLICY and
EVIDENCE_AND_HANDOFF were read from that same package; a version-suffixed package
name was unavailable and is not used as a substitute source.

| Physical/code object | Existing implementation/input | Actual scope |
|---|---|---|
| Thermal n/T nuclear inventory | `rei_fast_selected_20261028/nt_extension/inputs/nuclear/nuclear_network.py` and saved histories | Passive frozen reservoirs,18-family source, instantaneous all-bare thermalization; no physical fast stopping kernel |
| Decay/capture | External-source `model.py/config.json` | Evaluated beta lifetime expressions; illustrative fixed1/v capture continuation and bath dependence |
| Photon atomic hazards | External-source `atomic_sigma` and finite-bin fluxes | Common toy normalization with threshold-tail law; illustrative amplitudes |
| Photon nuclear/CR daughters | External-source `NUCLEAR/reservoirs/evaluate_operator` | Toy inclusive kernels, charge/spectator and energy ledgers; phenomenological ks/ke |
| Old M4 atomic bath | `rei_source_history_20261028/implementation/coupled.py:old_bath` | Actual saved photon/T/electron fields and angular geometry, H/He/Li provider fits, no new transport solve |
| Fast kinetic transport | `coupled.py:dynamic_new/compile_new/rhs_physical` | Dynamic B/U reservoir losses; no imported physical differential stopping or escape distribution |
| Observed HI photoionization | `sources/BECKER_BOLTON_2013.json` | Seven historical forest-inferred logGamma points, correlated statistical covariance, EOS shifts and separate Jeans systematics |
| Physical UVB prediction | `sources/PUCHWEIN_2019_FIDUCIAL.json` | Published59-row HI/HeI/HeII photoionization and heating moments; Compton raw excluded pending normalization |

The new calibration uses the published physical UVB template and actual
observational data, rather than fitting a renamed toy source. The authority's
frozen contract will specify the log-amplitude likelihood and interpolation.
Six atomic rate/heating moments do not recover an arbitrary spectrum, a Li rate,
MeV photodisintegration, CR yields, slowing, or charge-branch distributions.
Those missing inputs remain explicitly represented. Statistical amplitude
precision and numerical solver tolerances are separate quantities.

Optional old-pilot comparison would reconstruct `old_bath(...).photo[:,0]` and
add the old external-bin HI hazard once. The old saved clock is not invented:
if this comparison is selected, it must reuse the existing201-row clock and its
proper-time interpolation. The main calibrated-template construction does not
need this optional reconstruction, a donor IVP, or an old test replay.
