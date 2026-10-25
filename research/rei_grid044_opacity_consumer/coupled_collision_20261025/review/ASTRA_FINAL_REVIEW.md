# Independent final scientific review — coupled collision

**Decision: PASS_SCOPED.** The single authorized attempt passed all 19 checks with exit 0. This admits the instantaneous finite 40-state photon/target collision RHS, complete state Jacobian, and two independent source-amplitude columns for the frozen fixture. No repair or additional scientific run is required.

Reviewer `/root/collision_astra_final` did not implement the theory or code. Requested model was `gpt-6-astra`, high reasoning; actual runtime model identity is **UNEXPOSED**. Review used static source inspection, exact-byte binding checks, and standard-library arithmetic on saved arrays. It did not import the scientific modules, rerun the kernel/provider, integrate an IVP, or write externally. The only review outputs are this file and `VALIDATION.json`.

## Scientific findings

The reviewed event rate is r_ej = c nref sigma_ej y_lower N_j. Both photon-to-target and target-to-photon Jacobian blocks implement the derivatives of the same event rate, with the negative photon-target entries expected for depletion. The full matrix is not assumed Metzler; only the fixed-radiation target generator has that property. The independent scalar event oracle, numerical derivatives, all 40 coordinate faces, each of the 13 zero-lower-target edges, source-off/radiation-off distinction, absent n/T and neutron controls support the stated finite claim.

At independent fixed nref, energies and templates, the complete local normalization derivative is J_collision − Lambda I − z (grad Lambda)^T. The affine-Lambda oracle recomputes Lambda under each perturbation and checks all 1,600 active entries. This is a local supplied-gradient interface, not a model with nref algebraically derived from state. Reference rescaling changes nref, all normalized coordinates and source templates consistently and includes dot(r)/r. Proper-second units, Mb-to-m² conversion and the independent fixed-N source-amplitude derivative are consistent.

B stores cumulative ground-state ionization energy and is counted once. K records primary-electron energy injection, not solved heat. Xext records the source energy that also enters photons; its sign in the accounting invariant prevents double counting. Saved-array energy and isotope Jacobian projections agree independently. The explicit energy-drift helper adds E_dot·N once; this is supplied bookkeeping work, not directional transport evolution.

## Observed numerical evidence

| Check | Observed maximum | Frozen tolerance |
|---|---:|---:|
| Every active main Jacobian CS entry (402 entries) | 6.567124650813327e-16 | 2e-12 |
| Main CS structural-zero absolute residual | 0 | 0 |
| Centered source-off collision FD, row characteristic scale | 4.631090281577312e-13 | 2e-5 |
| General affine-Lambda CS (1,600 entries) | 4.1312944324879133e-16 | 2e-12 |
| Collision energy ledger | 1.0795584324889047e-16 | 3e-12 |
| Reference rescaling | 2.4469891755000166e-16 | 3e-12 |

The main photon-target block contains 112 active entries and target-photon block 196. Trace-T, Li6 and Li7 column coverage reports respectively 16, 32 and 32 active derivatives, with relative CS maxima 2.05821221560037e-16, 2.1623357232108828e-16 and 1.9906895443518133e-16. The oracle compares every active derivative against its own scale and checks structural zeros, so dominant species cannot mask missing rare-isotope entries. Source columns are differentiated with N fixed and match exactly in the reported arithmetic. Conservation gates use absolute physical term sums rather than a unit-sized denominator floor.

Independent standard-library checks using the saved arrays give energy-Jacobian projection 3.0948071386052865e-16, isotope-Jacobian projection 2.34986488665837e-17, source-energy projection 3.269192422640886e-17, and per-event energy partition 1.0106959345149214e-16. Different summation order explains the small variation from the child's residuals; byte equality is not required for independently calculated numerical residuals.

A dedicated sigma=0 numerical invocation was not run. Its zero-collision limit follows directly from the reviewed multiplicative event formulas; no extra empirical control is claimed. This does not block the finite result supported above.

## Exact evidence and portability

All 29 authorized source/input bindings match current bytes, saved snapshots and post-run hashes. All 36 receipt output hashes and all 21 provenance file hashes match. Saved targets exactly equal the contract's 21 synthetic target values; saved photon coordinates exactly equal one second times the saved two-source sum. Runtime files, provider and vendor assets are unit-relative. The absolute command path retained in the receipt records the observed execution location and is not a runtime input dependency.

| Artifact | SHA256 |
|---|---|
| `theory/IMPLEMENTATION_CONTRACT.json` | `b3b041733c8b1c0e3f8163f40c3be40913314b0c5565b394f910768b2329c8db` |
| `implementation/coupled_collision.py` | `c580747d4e12589ef1fac97bd7312ec340906926774be25a7fbd0412e0834d97` |
| `implementation/test_coupled_collision.py` | `eaa0928020ed3a2dfebaeab6776196afc08fbe139b91c0ffa12c3dc49d993e59` |
| `implementation/run_bounded_tests.py` | `5e076b6bee8d0afef59f6a13274acd3fe25b6b8c66c1888f8d8be57281632349` |
| `implementation/attempt01/RECEIPT.json` | `3eeb1a8f1c001bf71cf89d3abe7a3cdb363f318186837a8ada649a09d3f5f93e` |
| `implementation/attempt01/test_results.json` | `4bb38d7bf0c2b1e3dc4ab3f618c754cb8b51260080b14e4617d1cb45c2663710` |
| `implementation/attempt01/fixture_payload.json` | `97977f5394d586a9f867345597d6871c484ff84e219abb1caf1fc590402dd601` |

Full executed input/output hash maps are retained in `VALIDATION.json` and the raw receipt. The authoritative current contract is the b3b04173… final file; the earlier intermediate hash mentioned historically in the contract-review prose is not the executed binding.

## Budget, provenance and claim boundary

Attempt CPU was 0.20033199999999998 s and wall time 0.20596811699942918 s, under the 1 CPU s / 5 wall s attempt limits (0.8 s profiling soft timer). Cumulative source-campaign totals are 8.201436/10 CPU s and 8.23558345200945/20 wall s. One worker and one BLAS thread were used; imports/provider construction were charged within the child. There were zero new IVPs and zero old-suite replays. Main campaign remains 595.225063/600 CPU s and NO_MORE_IVPs. No allocation was reset.

The z=2 source formulas, amplitudes, escape factors and saved continuous normalizers are inherited actual inputs. The N=1 s source-exposure inventory and prior positive y are synthetic API fixtures, not evolved cosmic radiation or abundances. Their n=T=1e-20/Href values test positive trace inputs. GL2 packet sums were not renormalized: their saved ratios to continuous template rates are 0.99689419245057 and 0.9863501584763721. This review admits finite algebra, not continuum convergence or a physical history. Prior opacity evidence remains valid and untouched.

The selected physmath workflow remains version 1.0.0 with its original ten stages. Within the 87-node whole-goal DAG, this advances the selected original N3/N4 collision-interface obligation under REI-L1 partial, REI-EXP-OPACITY-CONSUMER and normalization binding under REI-EXP-SCENARIO. It does not close the generic WU event-compiler import obligation or a coupled L4 trajectory. L4_ready remains false, original N6 remains HOLD, whole-goal completion remains false and global physical completion remains null.

Physical n/T production and neutron-decay proton feed, CR/neutrino/inverse-beta coupling, LiI core/Auger, secondary-electron stopping/thermal deposition, continuum refinement and coupled target/radiation history remain OPEN. No strong no-go claim is made. There are no blocking findings or targeted repairs. Root can assemble and publish this scoped result under the user's existing authorization; this review does not authorize another scientific execution.
