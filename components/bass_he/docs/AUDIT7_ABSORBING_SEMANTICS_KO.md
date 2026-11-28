# AUDIT7 — DR10D upper-shell absorbing semantics

## Source/output alias

CPC 2023 Appendix A at Nmax=3 prints charge-exchange shell n=3 equal to the reported ionization cross section at both test energies:
- 0.5 keV/u: 0.3285e-17 cm^2 = 0.3285e-17 cm^2;
- 5.0 keV/u: 0.7708e-16 cm^2 = 0.7708e-16 cm^2.

The same Appendix A correlation diagram maps united-atom N=3 states to bound separated-atom states. In particular Q23 ends at united (3,2,0) but CORDIR maps that state to separated-center Z2 with n=2. Therefore upper-shell membership and bound-shell correlation are not disjoint physical labels.

## Structural absorbing bias

For one reversible two-state crossing encountered twice with one-pass probability p, uniform coherent phase averaging gives 2p(1-p). If the upper state is instead made a one-way absorbing Nmax sink, the first passage stores p and the second stores p of the surviving (1-p), so

P_sink = p + (1-p)p = p(2-p).

The structural difference is exactly

P_sink - P_reversible = p^2.

At p=1, the reversible final upper-state population is 0 after two complete swaps, while the absorbing sink is 1. Thus an Nmax sink is truncation bookkeeping, not the physical final population of the corresponding adiabatic/bound channel.

The current Q23 absorbing event in apply_eq50 reproduces p(2-p) exactly when all other transitions and rotation are disabled.

## Claim gate

Allowed:
- use the Nmax upper shell as an explicitly named truncation sink;
- reproduce Appendix-A author bookkeeping where shell-n3 and ionization exports alias;
- report sink population as a numerical truncation observable.

Forbidden:
- add Nmax sink and correlated bound capture as two disjoint physical channels;
- call the sink physical ionization without additional continuum authority;
- validate source Eq. (13) physical 3d-sigma population using the absorbing Nmax=3 model.

## Verification

- Wolfram: absorbing minus reversible = p^2 exactly.
- targeted channel-semantics tests: 6/6 PASS.
- local compatibility suite: 42 PASS.
- package build/install/import and compileall: PASS.
- wheel SHA-256: 18e12a78cd98dbd0192031e500c14eb5b174777651841c62ae3910b9edbee185.

Production CT2 and a disjoint physical capture/ionization partition remain closed.
