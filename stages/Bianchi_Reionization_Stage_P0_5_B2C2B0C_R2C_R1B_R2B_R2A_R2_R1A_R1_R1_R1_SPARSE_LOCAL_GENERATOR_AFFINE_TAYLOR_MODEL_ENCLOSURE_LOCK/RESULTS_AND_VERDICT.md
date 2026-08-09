# Results and durable verdict

## Verdict

```text
DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_R1_
SPARSE_LOCAL_SOURCE_AND_LOW_RANK_GLOBAL_COUPLING_PASS_
STATIC_SUBSTEP_CONTROL_ESCAPED_BY_ADMISSIBLE_STAGEWISE_SCHEDULE_
VALIDATED_DISCRETE_MAP_REMAINDER_NOT_CLOSED
```

This is a representation/discrete-map no-go, not a physical-history no-go.

## What passed

1. The node-local full-OTS branch source is exactly represented at one source
   evaluation site by two local first-order generators and one local mixed
   generator per node.
2. The canonical source-safe tangent rank lower bound `92003` is retained:
   `45923` rank-two node blocks and `157` rank-one blocks.
3. H and He nuclei directions vanish generator by generator.
4. The global owner-amplitude coupling has numerical rank three and maximum
   centered-difference/analytic-Jacobian relative discrepancy
   `7.95398642085213e-09`.
5. The eight supported owner/group allocation normalizations are each a local
   diagonal derivative plus one rank-one nonlocal mode. The conservative global
   rank upper bound is therefore `3+8=11`, only
   `1.1956131865265263e-04` of the local rank lower bound.
6. A Rust 1.94.1 `cdylib` evaluates the same outward sparse bounds. On the
   46,080-node load-bearing model it contains the Python result exactly with
   maximum ULP distance zero. It is an optional accelerator, not the authority.
7. Three shape lanes give the same accepted stagewise-control endpoint hash and
   pass all fixed-point, positivity, nuclei, owner, photon, thermal, PDS, and
   augmented OTS-energy gates.

## Decisive blocker

The locked MPRK22/SDIRK2 trial evaluates the source at four distinct
state/evaluation sites:

```text
population_t0
population_t1_predictor
thermal_tgamma
thermal_t1_final
```

No source-derived regularity law identifies the interval selection at those
four states with one fixed pair of node-local parameters. An explicitly
localized schedule that uses upper `(v,f)` endpoints before the half-step and
lower endpoints afterwards is therefore admissible under the current
source-safe differential inclusion.

The schedule passes all hard gates with local error
`1.1193423410560399e-04`, but its endpoint escapes the static four-corner hull
in `x_HeIII`:

```text
maximum absolute escape                  6.979149463209877e-12
maximum fraction of local static width   3.3079776479960625e-02
significantly escaping entries           9691
largest-escape node                       38382
```

The absolute displacement is small, but set containment is binary: the static
model is not a certificate.

## Evaluation-site cost

A source-safe discrete-map preflight needs at least one local polynomial block
at each of the four source evaluation sites, or a proved outward remainder that
covers their independent variation. Four blocks require only `16.875 MiB` for
local linear and mixed generators. The corresponding source-input rank lower
bound is `4*92003=368012`; the conservative global rank upper bound is `4*11=44`.
This is still sparse and computationally tractable.

## Plot reading

- `local_generator_norm_vs_temperature.png`: the source sensitivity is highly
  heterogeneous and follows the locked node hierarchy. A global generator
  cannot replace the local blocks.
- `static_corner_width_vs_stagewise_escape.png`: only `x_HeIII` visibly escapes,
  but it does so by about 3.3% of the static uncertainty width. This falsifies
  static-corner containment without implying a large physical uncertainty.
- `python_rust_sparse_bounds_runtime.png`: Rust is about 1.73 times faster only
  for this bounds hot loop. No whole-solver speedup is claimed.
- `table_event_distance_histogram.png`: the minimum knot distance is only
  `3.08424459328549e-04` in `ln T`, so event localization cannot be postponed
  to a coarse interval check.

## Authorization

```text
current bounded audit completed            true
instantaneous sparse source representation true
low-rank global coupling contract           true
continuous/discrete-map enclosure           false
production history                          false
production node chemistry                   false
R2C-R2                                      false
B2C2B                                       false
next stage                                  authorized
```
