# Scientific contract

Goal: provide deterministic, resumable, parallel composition of the sealed
four-site microstep over the first canonical BDF interval without changing its
numerical behavior.

Locked behavior:

- 26-event full-OTS registry and canonical first-interval forcing;
- MPRK22(1) plus Alexander SDIRK2, four source sites, three declared lanes;
- full versus two-half estimator and common all-lane acceptance;
- strict public widths `<2e-3`, validated local error `<2e-4`, and all returned
  implicit, positivity, H/He, photon, heat/escape, and energy gates;
- partition 2048, six bisections, one of 131072 minimum ticks;
- eventual event-localization target `2^-40` interval fraction once a certified
  callback exists.

There is no seed or ensemble. NaN/Inf, non-convergence, empty output, corrupt
state, missing lane, hash mismatch, fallback, or extrapolation is failure.

A first partition-2048 worker attempt must exactly reproduce predecessor
classification, widths, local error, table summary, ledgers, and endpoint arrays
in the same environment. Serial and parallel canonical payloads must match after
telemetry exclusion; interrupted/resumed bounded runs must match uninterrupted
record/state hashes. Three workers should materially reduce wall time without
relaxing a tolerance. Expected peak RSS is about 1.7 GiB plus supervisor/cache.

This stage does not authorize production chemistry, Bianchi sweeps,
recombination import, CAMB, source fitting, clipping, extrapolation, or a
background adapter. Outputs are `CANDIDATE_UNSEALED_LOCAL_EXECUTION`; only later
independent review may seal or promote them.
