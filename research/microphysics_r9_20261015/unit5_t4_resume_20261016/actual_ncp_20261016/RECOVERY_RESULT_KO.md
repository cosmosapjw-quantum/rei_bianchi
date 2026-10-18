# R9 Unit5 zero-H residual recovery — 2026-10-18

## Determination

The existing allocation and length-128 checkpoint were found on the NCP filesystem. The checkpoint is authentic and its internal reconstruction, cached seam, moment, Gram, ground-leakage, and node/weight checks passed. The separate zero-H residual diagnostic was launched from this checkpoint, but reached its original fixed deadline and terminated with `wall_limit` (supervisor exit `-9`). **No residual summary or residual array was produced.** The recovered terminal receipt is a real failed/deferred execution record, not a numerical residual result.

## Identity

Allocation `REI-R9-UNIT5-20261016T024854Z_99ca7c`; original deadline `2026-10-16T04:48:54.971486Z` (unchanged). The run restored the original 64-vector checkpoint and extended it to 128 with 70 new Hamiltonian actions (3 reconstruction + 3 cache samples + 64 extension). The residual recovery itself used zero H-actions and did not regenerate the checkpoint.

- NCP 128-checkpoint SHA-256: `b606fa60bce2f91899070772d0df9af8ab60d6dc5be642e396c3c53ace2c1dc8` (797,968,906 bytes); NPZ CRC check passed.
- Input data SHA-256: `7aa230b66d500e7637161589533eef4f3f4efdc13f4beafb7e28fd275ab82c5d`; input receipt: `3ae0c54716df1a7cfc1586a2641e1b461dffd3a721ed77daa4ca676bb0c0c3c8`; frozen V6 raw action: `31cdd14df59ffc6208561cb3c61ff4bd114240c380693ff5789e14441e7c091c`. These match the checkpoint metadata.
- Runner SHA-256 `2c19a310c7024c8e5249534a4b1e78acd1f30c1c44d9f9f00d78ad2abcc8926b`; repair evaluator `e253ad71baa58aec0e071a6bce63fbc481c0f85d72c318fffddb9cc9e0e1c722`; wrapper `60f5b2fb816cc4929961c03b2813afc69091d8167eab49f9808a4a8d5d343a5f`. All four relevant files exactly match the bytes published at PR151 head `6391f3f8bbf34f16c7b36013d424183786a51086`.

The existing 128 checkpoint archive is already recorded at Dropbox `/BASS_DERIVATION_DOSSIERS_20260912/REI_R9_UNIT5_CHECKPOINT128_20261016T034524Z.tar` and Drive file `1Evtyw3O7KK85JkVfMK37LgS0dGFAVRyV`, 798,863,360 bytes. Its prior backup receipt records local archive SHA and provider checksum/MD5 matches, but explicitly says no archive-byte download readback was done.

## Terminal recovery

The original 128 allocation failed in residual post-processing because `getattr(np, 'trapezoid', np.trapz)` eagerly evaluates the removed `np.trapz` default under NumPy 2.5.4. A separate zero-H diagnostic process then started at `04:21:27.946372Z`, used 1,647.067 seconds and 2,019,864 KiB peak RSS, and was stopped at `04:48:55.003957Z`, about 0.032 seconds after the immutable deadline. The terminal receipt says `status=deferred`, `reason=wall_limit`, `supervisor_exit_code=-9`. Diagnostic stdout/stderr are both empty. `residual_summary.json`, `residual.npz`, and `recovery_receipt.json` are absent. No matching Unit5/T4 process was present at this intake; unrelated HE28 pilot processes were left untouched.

## Numerical interpretation

The 128-step checkpoint's declared internal gates pass, including 9/9 reconstruction checks and 3/3 deterministic cached-operator seam checks. The separate 64→128 refinement rule is `0.001`; refinement is **HOLD** at all declared broadenings:

| eta (Eh) | spectrum L1/W | max CDF change/W | window mass change/W | gate |
|---:|---:|---:|---:|---|
| 0.05 | 0.07681738136 | 0.00368888744 | 0.00076874063 | HOLD |
| 0.1 | 0.03196466891 | 0.00140951400 | 0.00039140280 | HOLD |
| 0.2 | 0.00747650960 | 0.00026695849 | 0.00009540860 | HOLD |

`W=0.4243608179922081` is the finite retained-space daughter-state complement weight used to normalize this spectral measure. It is **not** an ionization probability. The claim remains a 92-orbital finite-space saved-complement projected Be+ spectrum. Physical continuum, exclusive ionization, electron capture, and basis closure are UNKNOWN/OPEN/HOLD.

## Next DAG

`READY_METHOD_REVIEW_ONLY`: assess the direct residual evaluator's cost and a bounded zero-H method using the existing length-128 checkpoint. No execution is included in this recovery, and any later allocation must be separate; the original deadline remains unchanged.
