# Independent numerical and evidence audit

## Conclusion

No blocking numerical defect was established in the admitted scalar-moment implementation or its saved evidence. The current provider receipt, manifest, and theory summary bind to the exact files reviewed. A low-severity input-guard mismatch remains. This audit does not cover the net bridge or independently assess the physics source.

## Evidence binding

- Provider SHA256: `9d40436fbebd2e99666cf15ed069ba4041693de32da843dc23b9672d59b12a16`.
- Verifier SHA256: `aeec5c1fe813cfc9df5e796ba17085a484714e52c16862e5077733496b234997`.
- Recomputed execution identity: `9f4874b0ec077126b707cd536a019d57d0c85585cc02452b369b2b627ff8369d`.
- All five implementation manifest entries and all three theory summary payload entries match their recorded sizes and SHA256.
- Theory script SHA256: `dbdb0fbc8f9950509fa737c226dae931e64ad3e88f6b4dfaa16a62877d8a08ec`; CHECKS SHA256: `6f51e6337171ace7e18b58a708d9bf5c186a90b274be2dba0995ec2c73648033`; derivation SHA256: `6930fb76b645144e8baef87cb927554a3dbc75495590f843c607c5715f8eba21`.

## Numerical conclusions

The `expn(2,x)` formula avoids the cancellation in `1-x exp(x) E1(x)` for the actual provider. Over the declared [2000,200000] K interval, x is approximately 0.789–78.911, and the saved moments remain normal, positive binary64 values. The saved direct 80-digit original-integrand quadrature has maximum relative discrepancy 2.1974065901747693e-14 at its three selected temperatures. This is consistent with the implementation; it is not a uniform physical or numerical error guarantee.

The theory checker originally reports tensor residuals with a denominator floor of 1. CHECK_SUMMARY explicitly corrects those saved residuals to true relative residuals. The numerical record therefore supports the summary only with that distinction retained.

A specific suspicion about overflow in `transfer_u(E,1)` at the largest finite binary64 energies was resolved by four new targeted quantile calls. All four returned the exact finite input endpoint, including binary64 maximum; the suspicion is rejected. The preserved check and observations identify the exact source hash. No existing suite, IVP, benchmark, or render was run.

## Finding N1 — low severity

**Object:** `lc_ionization.py:_real`.

**Evidence:** `np.asarray(values)` runs before checking dtype, so mixed boolean/numeric sequences such as `[True,0.5]` become numeric arrays. The function rejects pure boolean arrays but cannot reject boolean elements whose identity was already lost through coercion.

**Impact:** The docstring promise to reject bool is stronger than the actual element-level guard. Static reasoning establishes acceptance of `transfer_u(20.0,[True,0.5])`. Existing scientific calculations and saved receipts are unaffected by this narrow mismatch.

**Minimal correction:** Narrow the documented promise to boolean-typed arrays, or validate mixed input elements before NumPy coercion if strict element rejection is intended. Only an affected guard case is warranted.
