# AUDIT6 — DR10C same-system coherent-topology validation

## Source formulas

Janev, Pop-Jordanov & Solov'ev, J. Phys. B 30, L353-L360 (1997), give explicit He2+ + H / H+ + He+ channel probabilities.

For forward reaction (11), their Eq. (14) gives the non-interfering 2p-pi population

P(2p-pi)=(1-p23)(1-p12)(1-pS)(1-p_{2p-pi,3d-pi}) p_rot.

For inverse reaction (12), their Eq. (15) gives

P(2p-sigma)=p12(1-p12)(1-p23)
| exp[i(chi1'+gamma)]
 +(1-pS)sqrt(1-p_rot) exp[i(chi2'-gamma)] |^2.

Uniform averaging over the relative phase gives

Pbar(2p-sigma)=p12(1-p12)(1-p23)
[1+(1-pS)^2(1-p_rot)].

## Current scoped Eq. (50) identity

Using the exact current sparse apply_eq50 event ordering
[S23,Qother,Q12,Qm1,Q23], a 1s-sigma initial column and 2p-sigma final
element reduce algebraically to the same phase-averaged Eq. (15) formula.
Qother and Qm1 cancel from this matrix element.

A separate forward 2p-sigma initial / 2p-pi final element reduces exactly
to source Eq. (14); Qother is irrelevant there.

Wolfram symbolic checks return zero for both closed-form differences.
An independent numerical stress over 1000 random probability sets found a
maximum absolute Eq. (15) identity error of 5.551115123125783e-17 and
exact zero sensitivity to Qother/Qm1. The TDD tests also compare the
source formulas directly to apply_eq50 for 250 random cases per channel.

## Interpretation

This is a direct same-system topology validation of the current Markov
assembly for two non-absorbing Nmax=3 observables:
- inverse 1s-sigma -> 2p-sigma after uniform phase averaging;
- forward 2p-sigma -> 2p-pi, which is phase-free in source Eq. (14).

It does not prove full coherent equivalence. Source Eq. (13) for the
3d-sigma channel contains additional 3d-sigma->4f-sigma,
3d-sigma->4d-sigma and rotational terms outside the scoped Nmax=3
absorbing model, so Eq. (13) is deliberately not claimed validated.

## Verification

- Wolfram Eq. (15) phase-average symbolic difference: 0.
- Wolfram reduced Markov topology difference: 0.
- current exact transport/eQ50 blob numerical stress: 1000 cases,
  max identity error 5.551115123125783e-17.
- targeted new tests: 4/4 PASS.
- local compatibility suite on audit1 reconstruction with exact current
  transport.py and eq50_scoped.py blobs: 36 PASS.
- package build/install/import and compileall: PASS.
- wheel SHA-256: 8658ec2c4d1536d9d8cf6a62b495477bd17124641c584d1cc42465eb5986203b.

The parent audit5 branch remains the authority for its previously recorded
76-test full-suite verification; raw git clone is still unavailable in this
sandbox because github.com DNS resolution is blocked.
