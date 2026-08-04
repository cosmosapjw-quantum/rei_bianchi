# Authorized next stage — R2B MOMENT-CONSTRAINED-NODE-LIFT-HISTORY

Execute `P0.5-B2C2B0C-R2B-MOMENT-CONSTRAINED-NODE-LIFT-HISTORY` only from this R2A lock.

Required inheritance:

- keep the B2C2B0C global reduced-DAE history and exact photon ledger unchanged;
- keep the R2A macro mass, group-opacity, current-Gamma, transfer-rate, and cycling-capacity moments as hard constraints;
- lift the 18-macro distributions to the fixed B2C2B0A micro-node measure without independently solving quasi-static cloud abundance or redefining mass from opacity;
- preserve all three shape lanes and report their node-level KL/TV envelope;
- retain exact-zero G2b/G3 effective-HI and primary HeII/G3 channels;
- carry the tau=10 Myr all-case feasibility witness, while preserving tau=100/300 Myr failures as sensitivity constraints rather than clipping them;
- fail closed with node/macro dual certificates if the micro lift cannot satisfy all macro and global moments simultaneously.

R2B may begin the node-lift history only after creating its own durable pre-calculation directory, input lock, stage state, receipts, manifest, and SHA256SUMS. It must not start unresolved subtraction, front/Q_M, source/fesc, primordial recombination, or Bianchi feedback. `rec_bianchi` remains an external dependency requiring a deliberate SHA/adapter review when available.
