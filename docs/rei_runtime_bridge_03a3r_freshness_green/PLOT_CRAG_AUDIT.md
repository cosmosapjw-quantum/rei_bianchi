# Plot/CRAG audit — 03A3-R1 freshness and live-readback closeout

## Figure intent

`DAG_STATE.svg` is a governance-state diagram, not a runtime or physics plot. It separates five source/contract nodes that are complete from six downstream nodes that remain unexecuted or blocked.

## Correctness

The filled nodes correspond to exact source/CI evidence:

```text
PR #45 import firewall                    PASS
PR #47 authority-binding source           PASS
PR #48 freshness/live-readback RED        COMPLETE
PR #49 freshness/live-readback source     PASS
```

The dashed nodes match live readback:

```text
repository ruleset        not created
fixed global attempt ref  absent / HTTP 404
local lease               not created
native runtime            not run
first interval            no pass
provider review           not authorized
```

## Retrieval

The diagram preserves the governing distinction:

```text
source/CI barrier PASS != target-host execution PASS
native exit 0 != first canonical interval PASS
first interval PASS != REC/BASS provider compatibility
```

## Augmented hostile readings

Rejected interpretations:

1. `PR #49 PASS` means the GitHub ruleset is active.
   - False. Only the source capable of checking live rules is complete.
2. `03B` appears in the diagram, so the attempt has been reserved.
   - False. The exact ref remains absent.
3. Four completed source nodes imply most scientific work is complete.
   - False. Native execution, interval eligibility, and provider admission are load-bearing and unequally weighted.
4. Live GET immediately before POST is fully transactional against an administrator.
   - False. A narrow GET→POST race remains and must be recorded as a trusted-admin operational boundary.
5. REI runtime success would authorize every BASS state surface.
   - False. Frequency-integrated `J` and `G` states still require source-projection or spectral-closure certificates.

## Generation

The figure supports only this prediction:

```text
After a ruleset is created and independently read back, the next admissible action is a target-host static preflight that must stop before reservation.
```

It does not predict whether the target host, native runtime, first interval, or provider review will pass.

## Print-size disposition

The figure is suitable as a double-column engineering/status figure. At single-column width, the four explanatory lines at the bottom are the first elements likely to become too small; they should move to a caption before publication. This is not a scientific-paper figure and receives no publication-grade visual claim.

## Final classification

```text
SURVIVING CLAIM
  PASS_FRESHNESS_LIVE_READBACK_SOURCE

NARROWED CLAIM
  live readback materially reduces stale-receipt risk but is not a server-side transaction with the ref POST

WITHHELD CLAIMS
  PASS_ATTEMPT_REF_SERVER_PROTECTION
  PASS_TARGET_HOST_STATIC_PREFLIGHT
  PASS_NATIVE_RUNTIME
  PASS_FIRST_CANONICAL_INTERVAL
  PASS_PROVIDER_EXPORT
```
