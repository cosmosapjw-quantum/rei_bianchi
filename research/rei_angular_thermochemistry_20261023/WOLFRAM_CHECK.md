# Independent symbolic checks

Tool: Wolfram Language evaluator, invoked after the Wolfram context call.
The input differentiated the exact LRS characteristic E=exp(-eta)D and
mu=mu0 exp(-2b)/D, formed the signed shear/pressure matrices, and expanded
the local photo/RR and geometry energy ledgers. It returned:

| Expression | Exact symbolic result |
|---|---|
| (partial_eta E + (s/H) partial_b E)/E + 1 + (s/H)(3mu²-1) | 0 |
| Tr[diag(-s,-s,2s) diag(-Q/3,-Q/3,2Q/3)] | 2 Q s |
| Local photo/RR thermal + binding + photon + escape change | 0 |
| E' g + E g + 2(s/H) E g P2(mu) | 0 |
| Tr[sigma²] | 6 s² |
| Tr[pi²] | 2 Q²/3 |

Assumptions used: real b,eta,s,mu0; H>0; -1<=mu0<=1. Constants in local
events are independent formal symbols. The service printed undefined-global-
symbol warnings for those formal symbols and returned the exact expressions
above with isError=false. This is an algebraic check, not a numerical
trajectory, source-accuracy validation or proof of physical closure.

The complete returned text and source-search receipts are preserved in
intake_reionization_20261023/ROOT_SOURCE_RECEIPTS.json in the prepared
checkpoint archive. MATH_REVIEW.md contains a separate human-readable
independent derivation of the same identities and the quotient conditions.
