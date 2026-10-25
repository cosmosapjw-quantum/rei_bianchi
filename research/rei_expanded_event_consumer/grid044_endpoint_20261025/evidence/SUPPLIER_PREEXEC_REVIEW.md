# Independent supplier and scientific pre-execution review

Unit: `REI-GRID044-ENDPOINT-BINDING-01`  
Reviewer: `/root/supplier_intake`, independent of implementation agent `/root/normalization_review`  
Date: 2026-10-25 UTC  
Reviewed contract: `/workspace/scratch/9d364a030876/REI_BINDING_IMPLEMENTATION_CONTRACT.md`

## Decision

**CONDITIONAL PASS for the bounded endpoint implementation, with the exact donor field/axis clarification below required before scientific execution.** This is permission to implement and inspect the specified finite unit, not final scientific admission. No full-network, L4, time-domain, thermal-degradation, finite-mass, or native floating-point certification is inferred. No old provider suite, IVP, new83, or NCP was run for this review.

The selected REC endpoint and donor state can be combined as the stated instantaneous counterfactual source operator. They are not a new jointly evolved physical history. The CR code is reused only for its generic event energy ledger; the C23B spectral source is correctly excluded because its published redshifts and spectral support differ. WU is reused for incidence and ownership, not for synthetic-to-physical energy promotion. The HE and BASS missing inputs remain explicit, and the proposed VigilODE client is a finite endpoint adapter exercise rather than a D5 extension.

## Required clarification: actual donor field and axis

The contract's phrase “Read saved final row” is ambiguous and dangerous for this NPZ. Both abundance arrays have shape `(21, 201)`. The selected input must be:

```python
donor_x = npz["atomic_abundance_per_Href"][:, -1]
donor_labels = tuple(npz["atomic_state_labels"])
```

Do not use `atomic_scaled`, and do not select `[-1]` as a row. `atomic_scaled` removes isotope abundance factors; using it would make the He4 abundance approximately 1 instead of 0.082 and the Li6 abundance approximately 1 instead of 1e-14. Map by the exact labels because the saved donor orders Li7 before Li6 whereas REC orders Li6 before Li7. Assert all 21 labels, endpoint axes, and finiteness before evaluation. The saved neutron and both T populations are exactly zero and must remain zero.

Observed endpoint metadata (read from the immutable NPZ, without running a source or solver):

| Quantity | Saved value |
|---|---:|
| `a[-1]` | 0.33333333333333326 |
| `z[-1]` | 2.000000000000001 |
| `eta[-1]` | 1.9459101490553132 |
| `nH_ref_cm3[-1]` | 5.151254745827817e-6 |
| physical reference density, m^-3 | 5.151254745827817 |
| `proper_elapsed_s[-1]` | 9.742841244666013e16 |
| `temperature_K[-1]` | 14994.847774798709 |

The payload density 5.151254745827818 m^-3 agrees within rounding. Temperature is provenance only for this frozen ground-state photo-only response; no thermal RR fit is invoked.

## Additional interpretation requirements

1. **HE input is moments only.** The two quantities prepared for a future receiver are primary-electron number and first kinetic-energy moment. The photon-weighted means `P/Gamma` and `K/Gamma` do not define a monoenergetic spectrum or an angular law. Record spectrum, angular law, and finite-mass recoil distribution as null/OPEN. Retain degradation UNQUALIFIED, HE101 physical-provider false, C8 open, and the old exhausted reservation. Zero recoil in the selected stationary-target photo approximation is explicit model input; it is not a measured zero or finite-mass closure.
2. **The Rust positive point is positive only on supported isotope blocks.** A box built from actual per-isotope totals has zero-width neutron and T blocks. Keep those coordinates zero in the positive test. The actual boundary point is admissible. A finite but wrong Jacobian may pass the unchanged gateway and must fail the independent derivative/matrix check.
3. **BASS stress stocks and source rates are different objects.** Donor stress tensors have units J/m^3 and retain their signed components. New absorption energy, momentum, and anisotropic stress transfer would have rate units and require a qualified angular measure. Scalar `Gamma/P/K` do not provide that measure. Do not create observer-isotropic directions or infer a new stress-rate tensor from the stock snapshot. In particular, retain signed tensor components rather than interpreting every saved scalar named `p_*` as a nonnegative isotropic gas pressure.
4. **Reference-source notation must retain the expansion term.** For `dot n + 3 H n = S` and `dot r + 3 H r = R`, the normalized equation is `dot x=(S-x R)/r`. Thus the fixed-comoving reference `r=n_ref0*a^-3` has `R=0`, even though `dot r=-3 H r` is nonzero. `R` must not be replaced by `dot r`. The contract's differential `dF=(dS-R dx-x dR)/r-F dr/r` is correct when `dS` is taken in the caller's actual coordinates. REC already returns the normalized source; dividing by `r` again would be wrong.

## Scope and ownership checks

| Join | Admitted use in this unit | What remains open |
|---|---|---|
| WU | Unchanged catalog, chemical conservation, exact incidence, ownership registration, event source | Empirical qualification cannot be obtained from WU synthetic energy helpers |
| REC GRID044 | Stored 2x6x3 ground-state valence moments at z=2; unchanged `target_response` on actual selected populations | New opacity integration, full radiation/temperature/nuclear Jacobian, time evolution |
| CR | Generic explicit per-photo-event energy ledger, selected REC/REI external continuum | C23B spectral substitution, finite-mass/recoil physics, full radiative/thermal closure |
| HE | Number and kinetic-energy moment handoff metadata | Physical degradation, secondary spectrum, angular/recoil law, heating |
| BASS | Prescribed donor geometry and signed stress stock provenance | New absorption angular measure, four-force/stress rate, geometry feedback |
| VigilODE | Unchanged D5 gateway applied to new frozen 21-state linear f/J adapter at one time | Continuous physical domain, trajectory/error control, native FP certificate, full D5 requalification |

The 13 physical transition identities have a single extent owner each. The two selected photon continua contribute additively under that owner. An extra canonical physical-key check is necessary because WU's own key includes provider-domain text and cannot by itself reject two owners whose textual domains differ. A separately prescribed radiation injection is not an additional material photo-event or a second debit of the absorption energy. Binding, primary kinetic energy, and radiation sink are each counted once. Primary electrons enter the fast pool and are not reconstructed again as a thermal electron source.

The selected REC output has 25 **source outputs** and 23 derivative columns (21 populations plus 2 amplitudes); it is not a 25-state ODE. The main finite callback is 21-state. The stored `K` must participate independently in the energy check rather than being redefined as `P-chi*Gamma` by the consumer. The original source normalizations and 5..150 eV birth support remain unchanged. Ground-state isotope electronic equality is a declared approximation inherited from the supplier.

## Evidence inspected and exact dependency recovery

Inspected the frozen implementation contract; exact WU `chem_ledger.py`; CR `source_ledger.py`; VigilODE `gateway.rs`; the original GRID044 opacity contract and model configuration; `opacity_response.py`; saved payload metadata and NPZ endpoint fields; and the earlier six-provider handoffs and claim gates retained in `supplier_intake`.

The missing CR dependency was recovered byte-for-byte from the same source commit and delivered to the implementer:

- Repository: `cosmosapjw-quantum/bass_cr`
- Commit: `8d0a5c375589fbddadc2bb90c8117311c80bad09`
- Path: `research/cr_c23b_source_frame_20261023/implementation/boost_kernel.py`
- Git blob: `fec7ff4f1ca977bcfb5b09a4ce6a910d993a9a2a`
- SHA256: `ac2ba5f6b180b14cc52db962643c164391dcd6028e415ef5bca73aee8628a682`
- Size: 9,232 bytes
- Local path: `/workspace/scratch/9d364a030876/supplier_intake/bass_cr/research/cr_c23b_source_frame_20261023/implementation/boost_kernel.py`

Its provenance is appended to `supplier_intake/FETCH_MANIFEST.json`. The donor NPZ SHA256 is `ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b`; the original opacity archive SHA256 is `b12cc903a9d1d813416b2b77c2f7a8c74c1b657c5c85cf5a683e5e5c64001d9f`.

## Final-review gate

After execution, review exact source identities, chosen NPZ field/axis and labels, all 26 source contributions and actual zeros, charge/isotope/baryon incidence, row scaling without a unit floor, independent saved-K energy closure, normalized/SI conversions, all 23 derivative columns, variable-reference quotient controls, ownership and metadata rejection tests, finite callback raw outputs, wrong-J control, image labels and zeros, and cumulative resource receipts including failures. Final code/raw review must occur before publication. This pre-execution review alone does not satisfy that final gate.

Review activity comprised source reading, fixed-byte recovery, and saved-data inspection only. There was no old-suite replay, new integration, opacity recomputation, or IVP budget consumption. Native remote state remains unobservable where its surface is offline; no clean-state assertion is made about it.

## Pre-run implementation follow-up

An early read of the prepared implementation confirmed the correct donor field and axis, actual label mapping, retained zeros, and HE moment-only payload. The reviewer additionally identified a canonical-key weakness: including free-form `state_resolution` prose could admit a duplicate physical event even though actual ground state and electron pool were already encoded in WU side signatures. The author removed that redundant prose component, checks the frozen process/frame, and added a second duplicate-owner mutation for changed state prose. The author also changed `a` from a literal to the saved donor endpoint and added a separate negative control for omission of the differential quotient term `-F dr/r`; the existing negative control covers omission of `-xR/r` in the source itself. These changes were verified by source reading before execution. The implementation is ready for its bounded initial run once the root records the explicit field/axis clarification in the frozen contract. Final raw/output admission remains pending.
