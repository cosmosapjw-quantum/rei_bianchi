# Independent adversarial review

## Steelman

The stage no longer relies on static temporal coherence. It encloses the actual
four-site MPRK22-SDIRK2 map over the source-safe branch family, contains the
known stagewise-switch counterexample, passes a validated full-versus-two-half-
step error gate, and keeps event and ledger ownership explicit. The refinement
pattern is physically and numerically coherent.

## Strongest objection

The proof authority is project-policy binary64 outward arithmetic, not a fully
specified MPFR/MPFI environment. The stage also covers only one accepted
microstep and the load-bearing microstep is event-free. It cannot support a
whole-interval, Bianchi-background, or production-history claim.

## Risk ledger

| Priority | Risk | Current status | Minimal next support |
|---|---|---|---|
| P0 | accumulated wrapping over first canonical interval | open | adaptive composition with rank/remainder budget and accepted-step receipts |
| P0 | public widths could grow over many microsteps | open | interval-wide endpoint gate in all three lanes |
| P1 | real Hummer-Seaton crossing during the interval | semantics locked, not encountered | validated earliest-event localization and restart in the real history |
| P1 | binary64 outward policy depends on kernel semantics | bounded caveat | fixed platform receipt, independent replay, optional MPFR spot audit |
| P1 | raw interval ledgers are wide | structural exact authority locked | exact owner/event ledger accumulation throughout the interval |
| P2 | shape lanes currently coincide | only this microstep | preserve all lanes through interval composition; no post-hoc selection |
| P2 | optional Rust changes rounding/order | not load-bearing | Python containment and ULP/event parity before acceleration promotion |
| P3 | public README is stale | presentation issue | update only after remote merge and CI |

## Contrastive verdict

- **H1: production history ready** — rejected.
- **H2: uncertainty-qualified microstep ready; first interval next** — best
  supported.
- **H3: only exploratory numerics** — too pessimistic because local existence,
  nonlinear enclosure, local error, containment, event semantics and exact
  ledgers are now independently sealed.

## Verdict

A bounded durable pass is justified for one accepted FLRW microstep. The next
DAG node is adaptive composition across the first canonical interval, not a
Bianchi-family sweep and not production promotion.
