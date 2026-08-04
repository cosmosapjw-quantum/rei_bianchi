# Failure analysis

## What passed

- 46,080 diffuse parcel states were explicitly represented.
- 18 macro sink H/He states were explicitly represented.
- Photon partition residual: 5.229e-16.
- H nuclei residual: 6.774e-16.
- He nuclei residual: 6.431e-16.

## What failed

1. The quasi-static cloud abundance diverges when macro sink gas is photoionized.
2. Sink mass is strongly timestep dependent.
3. Four/eight-substep first-interval refinements have no feasible macro capacity allocation.
4. Conservative explicit node chemistry requires reaction limiting at percent level, far above the 1e-4 gate.
5. Macro redistribution moves up to 0.509 total variation from the raw absorber map.

## Why clipping is forbidden

Capping cloud abundance, forcing volume filling to one, or clipping x_HII would preserve neither the fixed R1 opacity nor the photoionization ledger. The correct repair is to change the closure state space, not the output values.
