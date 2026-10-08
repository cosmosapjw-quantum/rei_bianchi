# Actual accepted IGM → BASS finite history

`accepted_history.json` is a public-safe projection of the two stored PR86 accepted records, not a new simulation or synthetic history. Exact binary64 hex values preserve source epoch, gas fractions, and midpoint background. `adapter.extract(payload)` reads the pinned typed-state layout in full and rejects changed immutable input bytes; `validate(packet)` binds the projection to those exact records and rejects incompatible units, frame, conversion counts, clock, source/provider/closure, epoch, and continuity.

The source model is `manufactured_hhe_v1`, provider `grackle341_caseA_lowT_subset_v1`, closure `caseA_escape_C1_primary_only`. The accepted record/state evidence does not certify a physical reionization history. The unchanged source-pinned BASS modules are isolated in `source/`, with upstream license and recorded byte identities in `SOURCE_PIN.json`.

The finite prescribed cells use actual accepted midpoint gas and background, proper nuclei densities multiplied from cm⁻³ to m⁻³ once, and zero velocity. BASS `ElectronState` computes electron density and applies D=1 once. The clock uses t₀=0 and Δt=Δln(a)/Hmid from the original material midpoint surrogate; this is not an exact cosmological t(z) reconstruction. Frozen midpoint rate is a stated reconstruction, not an assertion about arbitrary between-node evolution.

The observer lies at the final edge with finite-window tail 0. Tail 1/8 is a separate supplied-boundary sensitivity. The depth outside this window remains `UNKNOWN`. BASS constants are source-owned (`sigma_T=6.6524587e-29 m²`), not silently replaced by IGM's slightly different thermal constant.

Run the focused receiver and independent Decimal70 oracle:

```sh
python3 research/igm_blockers_20261008/bass/verify.py --output /tmp/fresh-bass-output
```

Optionally add `--payload <original-private-PR86-payload-directory>` to verify that the immutable raw records project exactly to the checked-in fixture. Private input paths and raw checkpoint are not distributed. Each subprocess has CPU 900s, wall 1200s, one CPU, 2GiB compile or 512MiB numeric memory limits. The source-pinned clock consumer's tau, survival and probability mass are checked against an independent Decimal70 formula computed from original midpoint operands, including clock and density rounding. Ten negative cases and common-tail shifting/scaling pass. This performs no provider, RHS, photon observer, or new history calls.

`RESULT.json` preserves the observed focused build/run commands, exit codes, measured costs, arithmetic errors, source identities, and claim ceiling. Synthetic schemas under the earlier rate-export lane remain unchanged. No full BASS campaign is run.
