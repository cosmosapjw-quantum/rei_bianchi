# Scientific responsibilities in the REI checkout

The REI material state and its accepted proper-time update are the sole consumers for this integrated project. Develop new source, tests and science results here. Earlier upstream revisions remain provenance records.

| Local component | Supplies | Physical state owned at integration |
|---|---|---|
| [BASS and REC](bass_rec/README.md) | Selected R118 Rust geometry and photon characteristics, matched H/He recombination and a z=20 HMLA initial state | BASS owns photon propagation and the background used by its native call. REC owns its recombination calculation. REI owns the later H/He gas. |
| [WU088_HH](wu088_hh/README.md) | Atomic H/D charge-exchange rates, source snapshots, gas and binding work per reaction | REI owns gas stocks. The live D tracer is passive. The finite-cell input declares its own D/H. |
| [BASS_HE](bass_he/README.md) | Species-resolved energy accounting and F05 helium-line branching | For each host primary photon the accounting reads its original absorption once. Local OTS events are already paid in the F05 source. |
| [bass_cr](bass_cr/README.md) | Proper-frame injection, primary ionizations, nonthermal electron births | The REI receiver tracks the fast stock, ionic binding and threshold-convention difference independently. Heating needs a recipient-matched deposition model. |
| [VigilODE historical support](vigilode_reference/) | Pinned numerical crates used by selected historical HE/WU diagnostics | No gas, photon or CR state is owned here. The selected live R118 paths use their own numerics. |

Each component records source identities and third-party notices. The original WU and HE project trees include historical experiment entry points with their recorded external input prerequisites. The original CR release's large checkpoint bundle remains referenced by identity. The supported integrated entry point is `python scripts/run_unified_igm.py NEW_OUTPUT`.
