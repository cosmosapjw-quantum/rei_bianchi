# rei_bianchi tested research followthrough

Continue the published one-file branch without discarding its history. The
original `paired_budget.py` is byte-identical to its published source.
This change supplies focused tests, numerical mutations, a manifest, source
validator and local execution instructions; it does NOT implement the complete
thermochemical map or turn PR14 into a PASS.

From a materialized payload at a repository-shaped root:

```bash
python3 research/continuation_20260830/verify_payload.py --root . --repo /path/to/rei_bianchi
python3 -m pytest -q research/continuation_20260830/tests
```

The immutable package/source objects are checked, not mutable branch-tip
identity. `REMOTE_PUBLICATION.json` is separately committed metadata, outside
this manifest. Do not use obsolete base64 transports or rewrite old evidence.

Next: `REI-LOCAL-01_SOURCE_BOUND_PAIRED_MAP_ADAPTER`.
Current: `NO_PASS_FIRST_CANONICAL_INTERVAL`.
