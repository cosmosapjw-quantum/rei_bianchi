# Independent review: covariant transport and isotope-native D unit

**PASS_SCOPED_COMPONENTS_PILOT_GATE_PENDING.** The reviewed component implementation and evidence may be published. Full NCP launch admission has not yet been issued: the frozen short-interval refinement screen remains pending.

Base: `8aa6cd081f218e3a4ff6180a547c790df234a073`. Requested reviewer identity: `gpt-6-astra`, high reasoning; runtime identity was not independently observed. The reviewer read policy, contracts, finished source/test changes and actual raw outcomes. No source edits, git changes, tests, historical28-check replay or numerical runs were performed by the reviewer. Reviewed file hashes are recorded in the JSON companion.

## Transport decision

Fixed reference-energy N/Q/support state and physical E=R*q remove repeated projection onto fixed physical-energy nodes. Geometry keeps stored moments/support unchanged and accounts for physical photon work. Original source cells are integrated with GL8 intersections, with one angular normalization. Positive threshold-split moment reconstruction supplies the same node bank to BE photon survival, Gamma and heating inside the existing four-unknown cold Newton solve. The original gas RHS retains event ownership; there is no second photo update.

The fit edges remain distinct from binding energies. Common-cell N and physical-energy differences enter full/two-half comparison. Spectrum output reports actual local support and moments. Cold rates, source, geometry, IC, domains and physical tolerances are unchanged: target1e-5 and strict ceiling<2e-4; Newton1e-11; step/cumulative ledgers1e-10/1e-8; parity1e-12.

The first core test attempt passed6/7 and exposed one-ULP near-endpoint U/N loss from independent sums. The authorized bounded repair uses compensated count and positive endpoint-centered first moments, with represented moment bounds and stable centered means. This is equivalent arithmetic for the same positive measure. It introduces no tolerance clipping, broadened support or changed physics. The first failure is retained; the repaired target passes7/7. Final signed-family source-support assertions separately pass in the existing source test.

Six driver tests pass, and the new focused outer-run restart guard passes1/1, giving14 distinct new native tests. The initial six were preserved from actual tool output; their execution source SHA was not captured and they preceded the isolated core arithmetic repair. They are not labelled a byte-bound final combined suite. The independent core repair results and final focused checks are preserved separately.

Restart binding is explicitly the existing authoritative `run` contract: exact saved config plus compiled-source identity before reading V3 state. V3 stores N/Q/support, and rejects projected V2. Grid/reference/mode are bound by the config and source; standalone `read_checkpoint` is not claimed to bind arbitrary configurations. The focused test actually rejects changed transport grid, q_ref and source before history/rejection output or checkpoint mutation. The newly active `axbi_q_closure.rs` dependency is included in compiled identity.

This establishes the structural fix and component contracts. Two moments do not uniquely recover an arbitrary spectrum. Zero false-HeII events in the redshifted54.42eV delta control and conservation identities do not constitute full-history spectral convergence.

## D atomic and isotope-native RHS decision

The new standalone provider/RHS passes8/8 targeted tests on its first attempt; source/test/lib hashes match the receipt. Its selected H-equality model and threshold correction are conditional approximations. SI conversions and source floor/cap diagnostics are retained. The same explicit D threshold and H–D defect govern PI/CI/RR/CE and CX energy accounting. Photo moments are associated with one threshold; external bound moments retain an explicit caller/source obligation.

The isotope-native RHS uses the full isotope electron census, conserves nuclei/baryons/charge, leaves CX electron count unchanged and includes the changing thermal-particle term in its additive temperature derivative. RR thermal cooling is kept distinct from binding release. Free-free, CMB and expansion are not duplicated. Zero D is a no-op and legacy extra-species rejection is retained.

Inventory and ionic IC are explicit. The Cooke D/H example is an observation-conditioned ratio, not a new BBN calculation or matched REC donor. The fixed-nb H1/D/He4 helper includes2nD and labels its inventory scope. D remains outside production transport/evolution. No precision isotope-rate or cosmological D-history claim is admitted.

## Remaining executable gate

There are22 distinct passing new targeted tests across native transport/driver and D. Historical28 checks remain reused within their original scope.

At this component decision, q128 pilot attempt1 is running. Full launch requires actual completion of the frozen z20→19.8 energy128/256/512, time1e-5/2.5e-6 and angular8/16 screen, followed by review of its<=1e-3 comparisons and trend criterion. That screen is an empirical launch condition, not a continuum or full-history accuracy certificate. A running or incomplete pilot is not a pass.

Publish this component unit and continue the already authorized bounded pilots. Component review is closed; no optional adjacent repairs or extra tests are requested. Campaign admission will be reviewed when finished pilot evidence exists.
