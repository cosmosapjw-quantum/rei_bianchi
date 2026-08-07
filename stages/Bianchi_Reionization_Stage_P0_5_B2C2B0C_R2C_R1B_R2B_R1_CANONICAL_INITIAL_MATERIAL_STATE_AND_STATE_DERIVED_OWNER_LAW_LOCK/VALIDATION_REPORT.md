# Validation report

The final validation set comprises stage RED/GREEN tests, the 85-row full
forcing audit, Decimal-90 replay, Wolfram symbolic checks, adversarial tests,
repository-wide pytest, repository verifier, stage SHA-256 verification, ZIP
CRC, Git object verification, and a prerequisite-only bundle fetch/checkout.

The stage hard gate is `1e-11` for moment and closure residuals. The largest
load-bearing closure residual is `6.421e-12`. No sign, support, or structural
zero gate fails.
