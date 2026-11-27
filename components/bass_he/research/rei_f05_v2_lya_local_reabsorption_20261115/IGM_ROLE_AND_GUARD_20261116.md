# Escaped-photon energy guard and current IGM role

The native producer had compared the escaped-photon count interval directly to an energy interval in erg. Both lower bounds are zero in all 92,160 saved source rows, so a dimensionally wrong scale could pass interval intersection. The guard now converts with 40.813320 eV/photon and 1.602176634e-12 erg/eV and compares corresponding endpoints at the existing 6e-12 source-representation tolerance. Native equations, source channels, quadrature, the 2e-4 local-error gate and 2e-3 width gate are unchanged.

Author validation: six targeted tests passed, including all immutable 92,160 rows; maximum relative conversion difference 1.2733868152902887e-15. A distinct native agent with no inherited author history reviewed the diff and independently reran all nine tests, including the original receipt audit. Its long-double recomputation gave maximum relative conversion discrepancy 1.05919e-15. Review verdict: PASS_SCOPED_GUARD_REPAIR. Original CSV SHA256: 6acd17f0612738fa2954f3285b92b53d1444d8a4cc020375731d0557c0ba80ae. This representation check is not an outward-containment proof. The full native solver and private IVP were not rerun.

Reproduce the new checks from the repository root:

```sh
python3 -m unittest discover -s research/rei_f05_v2_lya_local_reabsorption_20261115/tests -p test_escape_energy.py -v
```

The active central scenario is PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1: primary-only Case-A escape, with CR/HH/RCT/secondary/molecules OFF. This F05 local OTS donor is a different scenario and is not imported into that baseline. Local OTS H/He absorption and heat are already in the original F05 RHS. Material quadrature nodes are not spatial cells and do not provide positions or null rays.

BASS_HE supplies source-owned microscopic energy/degradation partitions only when the central owner names the same scenario, energy/process domain, consumer function and physical result. No further source-only atlas is assigned by this synchronization. The canonical IGM DAG increment from this guard repair is zero; original source evidence and research/official tick distinctions remain unchanged. This isolated branch does not mutate the original owner branch or merge the result.
