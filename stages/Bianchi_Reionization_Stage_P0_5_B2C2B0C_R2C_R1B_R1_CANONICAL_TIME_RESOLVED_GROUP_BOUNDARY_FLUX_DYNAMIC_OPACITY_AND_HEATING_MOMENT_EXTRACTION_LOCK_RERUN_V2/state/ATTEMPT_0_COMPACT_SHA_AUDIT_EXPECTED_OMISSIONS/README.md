# Compact archive SHA audit

A naive recursive verification treated members intentionally omitted from compact bundles—nested full inputs, large split payloads and historical logs—as corruption. This was rejected. Every physically present member listed by an internal `SHA256SUMS` file matched its hash (`bad=0` in every inspected stage); missing entries were classified as expected compact omissions. Canonical ZIP bytes are separately locked by `INPUT_LOCK.json`.
