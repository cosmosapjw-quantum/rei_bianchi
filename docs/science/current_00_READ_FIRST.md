# Current science state — rei_bianchi

Current durable stage:

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-SPARSE-LOCAL-GENERATOR-AFFINE-TAYLOR-MODEL-ENCLOSURE-LOCK
DURABLE_FAIL_CLOSED_R2_R1A_R1_R1_R1_SPARSE_LOCAL_SOURCE_AND_LOW_RANK_GLOBAL_COUPLING_PASS_STATIC_SUBSTEP_CONTROL_ESCAPED_BY_ADMISSIBLE_STAGEWISE_SCHEDULE_VALIDATED_DISCRETE_MAP_REMAINDER_NOT_CLOSED
```

The previous two-global-coordinate rank defect is resolved at a single source
evaluation site. The 46,080-node source keeps two local linear generators and
one local mixed generator per node, preserving the source-safe tangent-rank
lower bound `92003`; owner amplitudes and the eight supported owner/group
normalizations add at most eleven named global modes.

This is not yet a continuous discrete-map certificate. MPRK22/SDIRK2 evaluates
the uncertain source at four distinct states. An admissible upper-to-lower
stagewise branch schedule passes all hard physics and numerical gates but exits
the static substep four-corner hull in `x_HeIII` by
`6.9791494632098772e-12` (`0.033079776479960625` of that local static width). The absolute shift is tiny, but set containment is binary.

The optional BASS Rust 1.94.1 bounds kernel is a differential accelerator only:
it encloses the Python oracle with maximum ULP distance zero and measures
`1.73049x` speedup on this kernel. It is not the
validated thermochemistry authority.

Production history, production node chemistry, `R2C-R2`, `B2C2B`, recombination
splice, CAMB transfer and Bianchi feedback remain unauthorized.

Next stage: `P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-R1-R1-R1-R1-EVALUATION-SITE-SPARSE-GENERATOR-VALIDATED-MPRK22-SDIRK2-DISCRETE-MAP-ENCLOSURE-LOCK`.
