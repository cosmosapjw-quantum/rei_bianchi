# Helium microphysics in rei_bianchi

The owner Python module `rei_bianchi.microphysics.he` classifies source-owned H/He photoionization energy and recombination-line emission. The original He–H collision and spectral numerical libraries remain under `src/bass_he` and `src/arseny_reimpl`. `arseny_reimpl` is the project's independent implementation based on published equations. The upstream readme and former build metadata are in `provenance/upstream`.

```python
from rei_bianchi.microphysics.he import primary_case_a_ledger

ledger = primary_case_a_ledger('HeI', photon_energy_ev=40.81332, absorbed_photons=1.)
print(ledger.heat_erg, ledger.binding_erg)
```

For the native Case-A driver, existing primary absorptions debit the photon reservoir and credit atomic binding and thermal energy. The cross-section fit cutoff and the binding energy may differ. For the F05 He II Lyα source, `f05_local_lya_ledger` uses the native cascade, two-photon branching, local absorption and recipient branching. Its photon and energy partitions already appear in the F05 OTS population and energy derivatives. Each interface labels its source and energy ownership explicitly. Neither interface evaluates a reaction cross section or predicts a new IVP.

## Joint energy envelopes for F05

For each of 92,160 saved source rows let \(h,y,s\) be the H I, He I and escaping photon counts integrated in gas proper time. The CSV supplies marginal count intervals for these channels and for emitted photons \(m\). Conservation adds \(m_\mathrm{lo}\le h+y+s\le m_\mathrm{hi}\). With \(E=40.813320\) eV and \(\epsilon=1.602176634\times10^{-12}\) erg/eV, the emitted energy partitions into

\[
B=\epsilon(\chi_H h+\chi_{He}y),\qquad Q=\epsilon[(E-\chi_H)h+(E-\chi_{He})y],\qquad E_{\rm esc}=\epsilon E s.
\]

For a linear objective with nonnegative weights one first assigns the three lower bounds. The maximizer fills remaining capacity by descending weight up to the largest feasible total. The minimizer fills by ascending weight up to the smallest feasible total. Exchanging two available allocations proves optimality for the stored box and sum constraint. For the local heat fraction the coefficient decreases from hydrogen to helium. The H maximum and He minimum are jointly attainable, as are the opposite extrema, because after eliminating escape the only additional constraint on \((h,y)\) is a lower and upper bound on \(h+y\). The sum over independent row polytopes therefore bounds the heat fraction of the total locally absorbed line energy. Physical correlations beyond the retained source intervals may tighten this range.

On source-native F05 research ticks 160–162 the allowed local heat share is **0.4212048–0.6493283** (17.19077–26.50125 eV per locally absorbed photon). The simultaneous emitted-energy upper bound is **2.721383×10⁴⁷ erg**. Adding the independent H I, He I and escape upper endpoint energies gives 5.174740×10⁴⁷ erg. Treating that sum as a common physical realization would overstate the allowed total by 90.151%. The source is a material quadrature over 46,080 nodes per interval. The installed source-qualified API keeps this result separate from the AXBI primary-only baseline.

From the `rei_bianchi` root, under its Python environment:

```sh
PYTHONPATH=src python3 components/bass_he/analysis/test_he_bridge.py
PYTHONPATH=src python3 components/bass_he/analysis/reduce_f05.py --output /tmp/F05_CONSERVED_ENERGY.json
PYTHONPATH=src python3 components/bass_he/analysis/check_vertices.py --output /tmp/F05_VERTEX_CHECK.json
```

`provenance/SOURCE_INVENTORY.json` maps all 11,621 source-revision entries to the owner paths and original Git blob identities. The transferred files include the historical code, tests, input tables, evidence, failed runs and tracked products. The older DR11E replay control records the approved donor ancestor and exact numerical dependency closure in `provenance/DR11E_PLAN_TRANSFER.json`, so the original Git history is unnecessary for the owner checkout. The separately published UV-background collection `source_original_v1.zip` includes material from third-party authors. Its archived version and retrieval provenance remain in the pinned producer. Archived studies that explicitly replay that external input require those original bytes; the two runtime interfaces and the F05 reduction run from the owner checkout alone.

The previous standalone repository's readme records the status of its independent code and legacy upstream terms. The third-party Grackle reference in `docs/atomic_reionization_handoff_20261004_v1/common/external_reference/grackle_3_4_1/` retains its bundled license. Source and scope are pinned to [BASS_HE PR155](https://github.com/cosmosapjw-quantum/BASS_HE/pull/155) at `b8300f57a5c36c109bf9a982769fb7ba76d250eb`.
