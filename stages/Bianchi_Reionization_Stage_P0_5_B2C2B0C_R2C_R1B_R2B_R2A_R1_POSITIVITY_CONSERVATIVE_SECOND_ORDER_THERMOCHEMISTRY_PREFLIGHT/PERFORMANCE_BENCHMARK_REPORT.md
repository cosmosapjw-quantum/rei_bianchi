# Performance benchmark report

The benchmark uses independent Python processes, excludes warm-up from the timed
region, and compares methods at matched accepted local accuracy.

| Method | Partition | Median warm time | Local error |
|---|---:|---:|---:|
| optimized MPRK22+SDIRK2 | 2048 | `0.791705 s` | `6.392782e-05` |
| backward Euler | 4096 | `8.017088 s` | `7.872276e-05` |

Speedup is `10.126360x`, above the predeclared `5x` gate.  Median
peak RSS is `542208 KiB` versus
`494316 KiB`; memory use is higher, so the
stage makes no memory-reduction claim.

Ablation:

- analytic SDIRK roots alone: `1.734179 s`;
- analytic BE predictor plus SDIRK roots: `0.791705 s`;
- predictor optimization speedup: `2.190437x`.
