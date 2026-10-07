Publication note: quoted hashes identify archived original bytes; current publication hashes are listed in ../PROVENANCE.json.

# Pre-run scientific clarifications
1. Limited DG records U0 before and after initial limiting. Both residuals are output: relative to post-limit U0 and to pre-limit U0. The latter must equal initial DeltaU plus SSP-weighted subsequent limiter changes; nothing is erased by reinitializing a reference.
2. Strictly interior bump quadrature nodes whose exponential reads zero are counted. For every such node, exp(exponent) < exp(-700); sum geometric quadrature weights * C * exp(-700) is an intentionally conservative omitted-number bound, and 100 times it bounds omitted initial energy. No positive floor is inserted. This only bounds initial quadrature readout omissions and makes no authoritative evolving-tail claim.
3. Raw minima remain in outputs. Positivity roundoff tolerance is only a reporting label, not permission to mutate the state or relax a conservation gate.
4. The P0 physical-E, log-spaced-grid interior-support derivative is Udot=-exp(-Delta x)*U. This differs from constant-g/log-x FV in the derivation note, because these are different reconstructions.
