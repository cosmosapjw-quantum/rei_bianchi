# Frozen PR242 dependency — text inspection only

Source: survey/github/PR242/implementation/caloric_branch.py, PR242 head3f299062a0d0d35c17f83a9e6081ca515e9d4c4c. Verbatim copy: unit/deps/caloric_branch.py. Git blob bc3ebd682c363afc7d5c36d164406086145b6964,5067bytes,SHA256ac5e5d50a454185550ba5614e50e914b7dad613795cf743347bd8b0b41c61aef.

| Surface | Text-observed contract |
|---|---|
| exact(value) | Accepts exact Fraction, int, or num/positive-den record; accidental binary floats reject |
| wire(value) | Fraction to string num/den record |
| CaloricBranch(knots, reference_volume_id, energy_store_id, provenance) | Frozen supplied monotone positive-temperature piecewise-affine caloric slice; provenance/convention labels required |
| knots, temperatures, energies, slopes, m0 | Exact immutable decoded knots, positive segment slopes and minimum slope |
| evaluate(temperature) | Exact interpolation within closed supplied temperature bracket |
| inverse(energy) | Exact inverse within supplied energy image |
| enclose_energy(Elo,Ehi,eta) | Conditional inverse enclosure; missing eta returns None |
| residual_radius(Tbar,Ebar,eE,eta) | Conditional residual-based radius; missing energy/EOS radius returns None |

The new module imports the exact dependency through deps.caloric_branch from the unit root. It uses its exposed exact decoder, arrays, slopes and inverse. The dependency has no directional derivative or callback pullback API; it is unchanged. No dependency import or execution occurred during this preparation.
