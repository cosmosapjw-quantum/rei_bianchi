# rei_bianchi post-audit first-interval bootstrap package

This directory publishes the machine-readable handoff for the complete first canonical FLRW thermochemistry interval.

```text
source audit HEAD  ace7d91af35bfefcc3a9bd7e83076aa8f8bf557e
source audit tree  c8167922076f52628b1f7243c9ebd8b40ebe7508
rec package         c82fecc0a44230c60408c144e030a7c05f0da3d7
current claim       NO_FULL_FIRST_INTERVAL_YET
next action         REI-AUDIT-COMPAT-00 then REI-INTERVAL-02
```

The exact `rec_bianchi` package is consumed only as monitoring/checkpoint metadata. No recombination rates, populations, histories, source-bound validator files, or surrogate are imported.

The ZIP is a transport container. Verify its SHA-256 and internal manifest, then use `CODEX_HANDOFF.md`. No production chemistry, primordial-to-CMB splice, CAMB transfer, Bianchi feedback, merge, or ready transition is authorized by this package.
