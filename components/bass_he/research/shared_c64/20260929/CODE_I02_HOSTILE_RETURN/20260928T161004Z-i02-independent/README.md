# CODE-I02 independent hostile return

Execution target: PR15 commit ac04d2a9e62120a0da4377ddf92451fde0c44431, tree 5697bfb7b2ceae5854499a8132b44e573672df85. Packet source: commit f48eae73612a29b37a47b86a21cba3b675eeb7a2, tree c421282dda256d47f8f4bd450c8d535bf990e886. The first findings were sealed before packet inspection.

Verdict: HOLD. Official test: 23 passed, RC 0. Hostile test: 54 passed, 10 failed, RC 1. Ten altered certificate payloads passed validation and reached the first real-anchor sentinel; no geometry action was completed. Exact identities, findings, commands, environment, and limits are in RETURN_REPORT.json. Target production code was not changed. Eq55 was not run or authorized.
