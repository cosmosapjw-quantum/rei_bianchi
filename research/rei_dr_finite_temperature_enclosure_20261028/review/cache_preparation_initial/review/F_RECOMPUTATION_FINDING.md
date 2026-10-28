# F-RECOMPUTATION — bounded per-instance memoization preparation

Actual basis: attempt02's repaired host-PID monitoring observed36 family CPU ticks at100Hz and stopped at the unchanged0.36CPU-s guard while the selected suite was running. No scientific assertion failed. Source inspection identifies repeated identical kernel(T,E) evaluations and second_bound(row,domain,loss), including repeated f0/d0/B2 dependencies over36 Taylor cases. This is a concrete recomputation cost diagnosis, not permission to weaken cases or acceptance.

New source only: dr_enclosure_cached.py adds two bounded per-instance OrderedDict caches, each at most256 entries. Kernel key contains exact energy and temperature endpoints plus arithmetic context signature; second-bound key contains actual decoded cs/es, current s/k, actual domain endpoints/loss and context signature. Context signature includes precision,Emin,Emax,clamp,rounding,capitals and every trap setting. Source-row validation and mixed-Arithmetic validation occur before cache lookup. Actual source/context mutation therefore selects a different key rather than using stale mathematical operands.

Cache storage contains immutable Decimal endpoint tuples only. Every cache hit and newly stored result returns a fresh Interval object. Mutating a returned Interval does not mutate the cached endpoints or later results. Arithmetic formulas, precision, exponent range, supported domain, positivity rules, all source rows, selected cases, oracle precision and acceptance assertions are unchanged. Existing tests are reused byte-for-byte via code_dr alias to the cached module; no added/deleted controls or changed tolerance.

New run_once_cached.py/execute_bounded_cached.py preserve PID-namespace handshakes and use attempt03/outer_numerical03. The cached plot reads only successful attempt03 and retains the once-only presentation path. Numerical whole target0.2,outer guard0.16,inner guard0.18,hardCPU1s,memory/wall unchanged. Outer polling0.01s and inner0.005s reduce unnecessary global scans; presentation1.5/1.4target/guard remains unchanged. Actual runtime fit is unmeasured. All previous originals, PIDNS versions and attempt01/02 remain unchanged.

Root accounting boundary: attempt02 wait4 .065662 is not full aborted-family cost. Retain conservative whole0.4 reservation and observed outer prefix.188753228 separately. Earlier failed whole.041656 plus both observed prefixes(.208878989) produce the root baseline21.654823051 from21.004288062. New proposed whole.2 plus tail.05 gives21.904823051,within22 but with UNKNOWN_NOT_ZERO retained. No closed/foreign budget is transferred or reopened, and no whole-session PASS is claimed.

Exact source diff: AUTHOR_CACHE_REPAIR.diff. Revised identities: CACHED_IDENTITIES.json. No scientific import, compile, tests, CAS, plot, renderer or retry ran during this preparation. Root and existing independent reviewer must inspect, publish identity/authority and issue the separate once-only dispatch before executing the cached command.

Future numerical command (not executed):

```bash
python -B -S code/execute_bounded_cached.py numerical --execute-authorized
```

Future presentation command (not dispatched):

```bash
python -B -S code/execute_bounded_cached.py presentation --execute-authorized
```
