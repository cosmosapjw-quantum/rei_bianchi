# Validation matrix

| Requirement | Check | Status | Evidence |
|---|---|---|---|
| import/API | targeted pytest | PASS | 15 stage tests |
| owner sum | unit + 340 all-row cases | PASS | closure CSV + independent validator |
| exact zeros | unit + owner registry | PASS | integer-zero source coefficients |
| capacity | 225 owner-correct cases | PASS | refinement matrix |
| regression | unsplit overcount | PASS | 20/20 expected reachable failures |
| refinement | 1/2/4/8 subdivision | PASS | max 2.688e-16 |
| node allocation | midpoint audits | PASS | no negative/zero-support violations |
| exact arithmetic | Decimal-90 | PASS | 340 cases |
| symbolic | Wolfram | PASS | zero residual identities |
| repository | `verify_repo.py` | PASS | 48 in-main artifacts verified |
| full regression | `pytest -q` | PASS | 80 passed |
| package/SHA/Git | post-pack immutable audit | RUN_AFTER_FINAL_MANIFEST | external delivery receipt |
