# Validation matrix — HERE_RUX03_EVENT_BRIDGE_02

All numerical criteria were declared in SCIENTIFIC_CONTRACT.md before candidate execution. Native target tests retain their original assertions; target and whole-workspace counts overlap.

| Gate | Actual result | Evidence in packet | Claim supported |
|---|---|---|---|
| Fixed default FT03 provider and owned event consumption | Source review; one provider call with manufactured HeIII RR delta passes actual AXI RHS checks | final source; build_v2/payload/logs/axisym_conditional.stdout.log | C01 |
| Same-evaluation diagnostic, units and rejected negative primitive | Three added tests pass; 11 conditional tests total | same log | C01/C02 |
| Existing FT03 semantics | 8 target tests pass | build_v2/payload/logs/ft03_controlled.stdout.log | C02 |
| Native build identity | 11 readback checks pass; clean exact commit and fresh target; original prelaunch validator accepts | build_v2/READBACK_VERIFICATION.json; payload/BUILD_RECEIPT.json | identity/execution provenance only |
| Full native regression | 176 passed, 0 failed; formatting passes | build_v2/VERIFY_TEST_SUMMARY.json; VERIFY_JOB.log | C02 |
| IC independent primitives | 22 components, max relative 1.0942794551292369e-12 <= 3e-11 | probe_v2_complete_inputs/initial_IC/VALIDATION.json; reference/oracle + generator | C03 |
| Cancellation-sensitive sources | Gross-normalized IC maximum 5.46413e-13 <= 3e-11 | same validation | C03 |
| H/He/charge/photon/energy and stage mapping | 48 IC +31 retained-final-stage check groups pass; max invariant 6.059918126088299e-15 <=1e-12 | probe_v2_complete_inputs/VALIDATION.json; raw requests/responses | C02/C03 |
| New changed-path IVP | DOP853 from IC, 257 RHS calls; 17 epochs; 22 output errors and state_scaled_max all0 | production_interval_v2/production_interval.json; production_dataset.npz | C04 |
| Changed-path ledgers | max local N 7.000969126733937e-15; E 1.7556755934167118e-16; all10 existing checks pass | same interval JSON | C04 |
| Independent final decision | Separate reviewer reads final claims, source and execution | review/DECISION.json; review/REVIEW_KO.md | scoped adoption only |

The retained final-state callback is diagnostic, not another integrated history. The independent Decimal oracle is a source-equation calculation, not execution of the candidate. Exact hashes do not establish physical admission. The interval runner retains scientific_admission=HOLD.
