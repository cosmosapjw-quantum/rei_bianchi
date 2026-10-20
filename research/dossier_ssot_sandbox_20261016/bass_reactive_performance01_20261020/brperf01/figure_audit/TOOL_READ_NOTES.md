# File-read note

One exploratory `rg` call used the glob `REPORT*` in `integration/`, where the
final report is named `README.md`. `rg` returned exit 2 for that unmatched path
while still printing the requested README matches. The actual README content
was available and used; no timing, physical-model run, test, or output figure
failed as a result. This is a harmless file-discovery miss, not a scientific or
numerical failure. The final audit source index pins the actual README.

The first rendered figure set completed successfully but had two clipped title
boxes and several close spacings. It was classified `REVISE`, not accepted.
The initial layout receipt is retained. Later bounded layout repairs left all
data and inference scopes unchanged, and the final render has no clipped text.
