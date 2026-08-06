# Claim-source audit — R2C-R1B

| ID | Claim | Evidence | Status |
|---|---|---|---|
| C1 | C2-Ray is explicitly photon conserving and couples ionization to time-averaged opacity through iteration. | Mellema et al. 2006, arXiv:astro-ph/0508416 | SUPPORTED; primary method |
| C2 | Multifrequency temperature evolution requires energy-weighted heating and stricter optical-depth-dependent convergence tests. | Friedrich et al. 2012, arXiv:1201.0602 | SUPPORTED; primary method |
| C3 | The inherited global ledger is group resolved but only interval averaged and global. | `input_canonical_direct_photon_ledger.csv` | SUPPORTED; canonical internal |
| C4 | R2B node `kappa` is constructed as `J/Phi` after projecting endpoint `J`. | `src/rei_bianchi/run_node_lift.py`; endpoint replay | SUPPORTED; canonical source plus `9.14e-16` replay |
| C5 | Endpoint-plus-integral constraints identify a unique positive forcing. | Exact rank/null proof and temporal witness | REFUTED |
| C6 | Exact pointwise macro/group current would identify node currents. | Spatial partition null witness | REFUTED |
| C7 | The fixed primary spectrum means photon count alone fixes heating. | Thin/thick absorbed-energy audit; Friedrich et al. 2012 | REFUTED in dynamic optically varying problem |
| C8 | Existing data prove no physical history exists. | No such evidence; endpoints are feasible | UNSUPPORTED and forbidden |
| C9 | A larger coupled generator is immediately required. | Identifiability deficit can be addressed by input extraction first | UNSUPPORTED escalation |
| C10 | `rec_bianchi/main` changed and requires deliberate adapter review. | GitHub connector SHA `ad316eb...`; monitoring policy | SUPPORTED; review not started |
