# Next low-temperature lithium experiment

This is a future experiment proposal using already collected evidence. It adds no current validation, execution stage, or automatic activation of a cold Li network. The current unit supplies H/He/D acceleration and a conditional Li6/Li7 coefficient component; its 10^-5 interpolation target is separate from source-fit uncertainty, isotope-model error, and omitted-process error.

Use the existing PR151 photo-response functional and the new per-channel Badnell RR/DR coefficients in a prescribed-background number experiment for separately conserved Li6 and Li7. Keep the explicit `ElementalElectronicEquality` policy and caller-supplied charge populations, T(t), n_e(t), and radiation field. The prior photo calculation is a radiation functional, so its cross-section/source/energy conventions remain owned by that provider. It is not moved into a T-only table.

RR q=1,2,3 starts at 10,40,90 K respectively; DR q=1,2 uses the corresponding intervals and bare-ion DR is structurally zero. A complete four-charge prescribed-temperature experiment can use T≥90 K while respecting the appropriate upper domains. Below 90 K, identify every populated or reachable charge channel and its source support rather than silently dropping a required recombination channel. Voronov CI lower electron temperatures remain [1,4,5] eV: the current provider cannot supply physically admitted cold-CI values by extrapolation.

## A constructive CI-omission criterion

Let p_A(t) be the four charge fractions for an isotope A with nonzero total abundance. On a prescribed background, let Q_0(t) contain the retained photo/RR/DR transitions and ΔQ(t) contain omitted CI transitions. Assume both Q_0 and Q=Q_0+ΔQ are finite, integrable Markov generators with nonnegative off-diagonal entries and zero column sums. Assume identical initial populations and actual source-supported finite bounds 0≤C_q(T(t))≤B_q(t) on the missing CI coefficients.

Variation of constants with the full generator's ℓ1-contractive propagator gives

    ||p_A(t)-p_A,0(t)||_1
      ≤ 2 ∫_0^t n_e(s) Σ_(q=0)^2 B_q(s) p_A,0,q(s) ds
      ≤ 2 ∫_0^t n_e(s) max_q B_q(s) ds.

The first bound retains the computed occupation of the omitted channel; either bound can be capped at 2, the maximum ℓ1 distance of two probability vectors. It bounds only the CI omission under these hypotheses. A coupled temperature/electron/radiation evolution needs an additional stability argument; the prescribed-background bound does not automatically transfer to it.

A Maxwellian threshold factor alone is insufficient to establish B_q. One possible future construction is an actual source-supported cross-section envelope σ_q(E)≤σ_max,q for E≥χ_q. Integrating that constant envelope yields

    B_q(T) = σ_max,q sqrt[8 k_B T/(π m_e)]
             × (1+χ_q/(k_B T)) exp[-χ_q/(k_B T)].

The present collected sources do not supply or validate such a global envelope. This formula specifies the needed future evidence; it supplies no current numerical bound or permission to set cold CI to zero. Once finite B_q is sourced, compare the integrated omission bound with a separately chosen population-error target and run a small direct-versus-tabulated retained-process control.

## Energy and native-state continuation

Photo heating must use the existing provider's actual absorbed-photon and threshold bookkeeping. RR/DR number coefficients do not determine recombining-electron kinetic-energy loss or emitted-energy moments; source those moments before attaching a complete thermal/photon ledger. The collected neutral isotope-shift magnitude does not provide ionic RR/DR energy moments, and its subtraction sign remains unresolved. Do not patch source fit thresholds from it.

Then integrate eight Li charge states (A=6,7; q=0…3) into the native state/electron/EOS interfaces with explicit BBN inventory mapping. Preserve the prior omitted Li6 reservoir rather than treating it as zero or importing a conditional charge initialization automatically. Check per-isotope nuclei, baryon-weighted counts, and charge/electron accounting. Li8/Li9 and Be7 daughter sources require their own nuclear-decay closure if that later scope is selected.

## Interpreting the forthcoming C8 measurements

Report direct/prepared/table scalar costs separately from SoA batch and parallel costs. Compare parallel against the matching serial batch to isolate the threading effect. Use the same input distribution and outputs, retain repeated-run variation, and include construction B in the crossover N>B/(c_direct-c_lookup) only when the measured denominator is positive. If no tested crossover occurs, report that workload result directly.

H/He coefficient/mask payload is 9,109,624 bytes; RSS is a separate measurement. Share immutable tables and choose chunks/workers using measured overhead. Large available host RAM is not a reason to duplicate tables. Local coefficient speedup does not determine end-to-end cosmological speedup without the rate-evaluation runtime fraction f; Amdahl's relation is 1/(1-f+f/s). Exact duplicate-rate removal, interpolation acceleration, data layout, and threading are distinct contributions. No SIMD claim follows without corresponding execution evidence.

Evidence reused: `evidence/intake/LI_PRIOR_PR.json`, `evidence/sources/SOURCE_REGISTRY.json`, `evidence/sources/SOURCE_NOTES.md`, `data/lithium_coefficients.json`, and `THEORY.md` R5–R10. No new source lookup or numerical execution was performed for this proposal.
