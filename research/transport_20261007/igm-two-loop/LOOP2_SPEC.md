# Second-loop experiment, fixed before execution

This experiment begins only after the first-loop panel and tail oracles pass. It uses the new primitives, with prescribed opacity and no evolving gas. It does not replace the production lower-boundary exporter.

## Continuous stock export

Use the existing FLRW characteristic coordinate eta=s+ln(E/eV), cutoff Ec=13.6 eV, s0=-ln(13), initial support E in [13.7,20] eV, N0=1e-8 photons/H. The small inventory is an explicit manufactured control, not the source of the original cosmological certificate. Ordinary and right-front closures use beta=0 and 2; a tail case uses ln(N0)=-750. Rebuild temporary integration cuts at the actual moving boundary on each observation. No persistent node carries a whole packet to its crossing time. Test delta-s below, at and above ln(13.7/13.6), and complete export. Compare transparent owners to independent continuous integrals. A separate prescribed-opacity test may use lambda_HI(eta)=2 exp[-3(eta-s0-ln(Ec))], with no evolving gas claim.

## Source birth, shutoff and quadratic export onset

An initially empty, transparent radiation field has constant q=1e-8 photons/H/deta/ds inside the physical band [13.7,20] eV, switched on at s=0. At a fixed eta, source entry is max(0,eta-ln(Emax)); exit is min(s,eta-ln(Emin)); cutoff crossing is eta-ln(Ec). Split all events and integrate source-bearing and source-free segments with the same owner kernel.

Let d=ln(Emin/Ec), D=ln(Emax/Emin), w=max(0,s-d). Direct continuum integration gives

    out_N = q [min(w,D)^2/2 + D max(w-D,0)],
    out_E = epsilon Ec out_N,
    injected_N = q s D,
    injected_E = q epsilon (Emax-Emin) s.

In particular the onset is quadratic, with zero initial flux, not a finite node-weight jump. The source-on lower trace is locally proportional to eta-ln(Emin). This motivates the second-loop left-front family y exp(beta y), preserving the first loop's ordinary/right-front admission limits. A left-front interior restriction must retain the parent taper rather than fabricate a new zero.

## Moment-dependent observable extension

For positive spectra supported on energy [a,b], total N and mean energy mu, convexity gives the sharp interval

    N/mu^3 <= integral E^-3 dN
      <= N [(b-mu)/a^3 + (mu-a)/b^3]/(b-a).

The interval width bounds the difference between any two spectra with identical N and U. Test endpoint and mean atom sharpness, positive interior mixtures, exact moment-preserving rearrangements and decreasing support width. Sum bounds over exact panel restrictions to test refinement. This is a theorem/control for E^-3, not a certified Verner cross-section envelope; actual species cutoffs and kernel-specific envelopes remain a separate next gate.

## Acceptance and work limits

Use the contract's original count/energy allowances, adding any explicit underflow readout bound. For source-free controls emitted_N and emitted_E remain zero; do not replace the original denominator with initial inventory. For every positive independent owner, compare abs(expm1(candidate_log - high_precision_log_reference)) <= 3e-12, including zero-readout tails. An exact reference zero requires exact emptiness. No result-dependent absolute floor. Run candidate numerical batches sequentially, at most 120 CPU/180 wall seconds per component, and measure compilation separately. Keep live integration sites below 4096; list actual counts and separate oracle work. First failed attempts remain in evidence. New observations must evaluate the original same control, not feed back to a primary trajectory.

Output: raw CSV/JSON, regression tests, independently reviewed scope decision, and next DAG. Production long-history 8/37 failures, sharp-wake shape coverage beyond |beta|=128, gas feedback and repeated projection remain open unless explicitly executed and admitted.

## Stored event coordinates (clarified before the integrated experiment)

For source topology, the supplied inputs are binary64 Lmin=ln(13.7), Lmax=ln(20), Lc=ln(13.6), and each stored boundary B=fl(h+Lc). The exact-input outflow oracle uses w=max(0,Decimal(B)-Decimal(Lmin)) and D=Decimal(Lmax)-Decimal(Lmin). B<=Lmin means exact empty swept measure for these supplied coordinates. Report B-(h+Lc) in high precision separately. This does not assert arbitrary real-time onset accuracy beneath representable geometry. Physical cutoff energy remains the explicit 13.6-eV anchor; its energy roundtrip is audited separately. Cumulative-source ledgers continue to use the supplied h and log-band width, so geometry rounding cannot be hidden by an alternate ledger.

The selected source observations are h=0,d/2,d,d+0.001,d+0.002,d+0.004,0.1,0.5,0.8 with d=Lmin-Lc, at one and two Gauss8 subdivisions per event interval. Stock sweeps use h=0,0.003,0.008,0.1,0.5, parts=1 and8, all three front families and beta=0,2, logN=ln(1e-8) and-750. The optional prescribed-opacity panel experiment is not executed; opacity coverage is limited to first-loop single-characteristic controls. Observable refinement uses1,2,4,8,16,32 child intervals.
