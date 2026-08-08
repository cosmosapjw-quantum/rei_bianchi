# Attempt 1 — binary-float literal equality false negative

The first source-table test compared parsed decimal strings to Python binary-float spellings such as `0.28500000000000003` with exact `==`.  The CSV correctly stored `0.285`, but exact binary representation made the test fail.  The scientific data were unchanged.  The validator was corrected to compare the source decimal values with `atol=1e-15`, `rtol=0`.
