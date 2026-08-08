# Validation matrix

| Gate | Threshold | Result | Status |
|---|---:|---:|---|
| local error, partition 2048 | `<2e-4` | `6.392782e-05` | PASS |
| H nuclei | `<1e-11` | `4.397361e-16` | PASS |
| He nuclei | `<1e-11` | `4.504562e-16` | PASS |
| owner closure | `<1e-11` | `1.953502e-16` | PASS |
| photon closure | `<1e-8` | `1.449900e-16` | PASS |
| thermal balance | `<1e-10` | `9.999943e-13` | PASS |
| PDS RHS reconstruction | `<1e-11` | `5.069599e-16` | PASS |
| strict positivity | `>0` | `1.408422e-154` | PASS |
| science parity | `<1e-10` | `8.792966e-13` | PASS |
| matched-accuracy speedup | `>=5x` | `10.126360x` | PASS |
| memory reduction | none required after primary speed gate | `-0.096885` | NO CLAIM |
| event-resolved PDS ownership | required for history | not identified | BLOCKS HISTORY |
