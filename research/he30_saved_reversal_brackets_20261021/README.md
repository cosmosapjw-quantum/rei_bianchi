# HE30 contribution: D8 late shear-reversal brackets

REI closure commit `744438f4512c7df1646aad0136ddc435b27200b0` left D8 as the next saved-data task. BASS_HE has completed that bounded task using the same D3 archive, with **zero ODE calls, zero root solves and no interpolation**. Independent delta review: PASS_SCOPED_PRELIMINARY.

This additive directory contains the script, four interval rows and independent review. It does not modify the original pilot, AGE results, source closure or existing DAG. Merge/integration remains reviewable.

Source consumer/data: [BASS_HE PR83](https://github.com/cosmosapjw-quantum/BASS_HE/pull/83), reviewed release `fb3146b94093776cad88e68cffb89b6559a405b3`. [Main report and four figures](https://github.com/cosmosapjw-quantum/BASS_HE/tree/fb3146b94093776cad88e68cffb89b6559a405b3/research/he30_z2_continuation_20261021).

All four cases have initial Sigma_F=.003 and P_r=-.001.

| Initial P_m | Open mean-redshift interval | Earlier/later saved index |
|---:|---:|---:|
| -.0003 | (2.8729833462, 2.9353050508) | 135/136 |
| -.0001 | (2.5192408407, 2.5758703349) | 141/142 |
| 0 | (2.3546766722, 2.4086580994) | 144/145 |
| +.0001 | (2.1978077332, 2.2492649203) | 147/148 |

Signed S=sqrt(6)s/H is positive at the earlier sample (z_upper) and negative at the later sample (z_lower). These are intervals between numerical stored samples, not precise event roots, uniqueness proofs, or rigorous continuum error enclosures. The 25-point plane has four sampled positive-to-negative transitions in the tail, no sampled reverse transition and no exact-zero sample.

Reproduce using the existing compact data in a BASS_HE checkout:

```bash
python3 research/he30_saved_reversal_brackets_20261021/src/late_reversal_brackets.py \
  --catalog /path/to/BASS_HE/research/he30_z2_continuation_20261021/results/CATALOG.json \
  --histories /path/to/BASS_HE/research/he30_z2_continuation_20261021/results/histories.npz \
  --out /tmp/rei_he30_d8
```

Source D3 archive SHA256 `7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498`; compact NPZ SHA256 `d4258bc58948b318df2b9d5ea7ceca6258eac62147aececc6ec10068987b6c6c`. The HE compact publication commit and original REI source/results publication commit are separate JSON fields.

Matter is the nonbaryonic massive collisionless component; radiation is photon plus massless neutrino. No native H/He chemistry is added. No additional science workload or benchmark is needed to consume this result.
