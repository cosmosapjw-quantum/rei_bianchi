1. **P2 — Intermediate underflow destroys a representable characteristic component.** At [bianchi_i.rs:149](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/bianchi_i.rs:149), finite zero is accepted after multiplying nonzero operands. Executed input:
   - `a0=[1e-200,1,1e100]`, `a1=[1e100,1e100,1]`
   - `E0=1e200`, `e0=[1e-100,1,0]`
   
   Transport returns `e1_x=0` instead of representable `1e-300`; conserved `q_x` changes from `1e-100` to zero, and inverse transport does not recover it. **Smallest repair:** evaluate scaled components without destructive intermediate underflow, or reject unrepresentable intermediates before returning a successful ray.

2. **P2 — Positive energy and density underflows return successful zero values.** [angular_photons.rs:38](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/angular_photons.rs:38) accepts `E=1e-200`, `count=1e-200` and deposits zero energy while retaining positive count. [angular_photons.rs:97](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/angular_photons.rs:97) returns `Ok(0)` for positive count `1e-200` divided by volume `1e200`. Both were executed and contradict the frozen underflow-rejection requirement. **Smallest repair:** distinguish genuine zero-count results from zero produced by positive product/quotient underflow.

3. **P2 — Ordinary accumulation violates the declared conservation tolerance.** The additions at [angular_photons.rs:16](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/angular_photons.rs:16), used by state totals and bin deposition, lose small contributions depending on grouping. With one `(E=10,count=1)` packet followed by 4,096 `(E=20,count=2^-54)` packets:
   
   | Quantity | State total | Remapped total |
   |---|---:|---:|
   | Count | `1.00000000000000000` | `1.00000000000022737` |
   | Energy | `10.0000000000072760` | `10.0000000000045475` |
   
   Both discrepancies exceed `5e-14` relative tolerance; the remapped values match the exactly representable reference totals here. **Smallest repair:** compensated accumulation for state totals and each bin/reservoir, with consistent final reduction.

4. **P2 — Accepted public direction fields change energy under identity transport.** [bianchi_i.rs:133](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/bianchi_i.rs:133) discards the normalized result of `new`; [angular_photons.rs:28](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/angular_photons.rs:28) likewise preserves the original ray. A public-field ray with `E=1`, `direction=[1+5e-13,0,0]` passes validation and `PhotonPacket::new`. Identity transport returns energy `1.0000000000005`; isotropic derivative evaluation also produces spurious direction drift. **Smallest repair:** consistently use the canonicalized ray, or reject noncanonical public-field states before calculation.

5. **P2 — Derivative cancellation branch erases nonzero weak anisotropy.** At [bianchi_i.rs:198](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/bianchi_i.rs:198), `e=[0.6,0.8,0]`, `H=[1,1+4*EPSILON,1]` returns direction derivatives `[0,0,0]`; the rational characteristic gives approximately `[3.4106051e-16,-2.5579538e-16,0]`. This exceeds the frozen component-relative comparison tolerance. **Qualification:** the discrepancy is only a few ulps of the Hubble scale; it is a weak-anisotropy accuracy defect, not a demonstrated large transport error. The frozen rational zero case passes, but does not validate clipping nearby nonzero derivatives. **Smallest repair:** cancellation-aware differential evaluation with a regression that preserves resolved shear while retaining the frozen rational case.

**Directly executed evidence:** the frozen validator passed **8/8 tests**. The separate linked Rust probe reproduced every finding above and confirmed caller immutability for the tested rejection. Retained artifacts:

- [Probe source](/tmp/rei-f06-review-cl_4ff4ee1c-boundaries.rs)
- [Exact argv, environment, hashes and exit codes](/tmp/rei-f06-review-cl_4ff4ee1c.argv.json)
- [Raw probe output](/tmp/rei-f06-review-cl_4ff4ee1c.output.txt)

| Review cell | Scoped status |
|---|---|
| Frozen analytic points, isotropic/axis limits, occupation | PASS: executed fixtures |
| General characteristic conservation/inverse | FAIL: finding 1 |
| Positive derived-value representability | FAIL: finding 2 |
| Count/energy conservation tolerance | FAIL: finding 3 |
| Public-field validity/identity | FAIL: finding 4 |
| Differential characteristic | Frozen case PASS; weak-anisotropy boundary FAIL |
| Guard ownership and midpoint refinement | PASS: executed frozen fixtures |
| Rejection immutability | PASS: tested rejection |
| Coupled history, continuum spectrum, physical scenarios | NOT_EVALUATED; outside scope |

HEAD matched `6279036f06c9ba4d47574beab90b48fc2c6f9ba7`; all six review-scope hashes matched before and after review. No candidate or validator edits, Git operations, nested agents, or local inference. Parent owns repair, external validation, and admission.

<oai-mem-citation>
<citation_entries>
MEMORY.md:3371-3371|note=[kept review within trusted local scientific correctness scope]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>
