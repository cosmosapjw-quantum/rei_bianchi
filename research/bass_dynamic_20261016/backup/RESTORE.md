# REI BASS dynamic source recovery

`source_delta.bundle` contains implementation commit
`1f8619c27c1d2b7f13e1c05cf3819c9766cd38f3` and requires exact REI PR150
base `7cb4ac678be019b736e85db76dfbdc7c51e380e9`. The source and raw
release evidence can be independently recovered with a fresh Git repository:

```
git init restored
git -C restored remote add origin https://github.com/cosmosapjw-quantum/rei_bianchi.git
git -C restored fetch origin 7cb4ac678be019b736e85db76dfbdc7c51e380e9
git -C restored bundle verify ../source_delta.bundle
git -C restored fetch ../source_delta.bundle HEAD:refs/heads/restored
git -C restored checkout restored
git -C restored rev-parse HEAD
git -C restored rev-parse HEAD^{tree}
```

The expected implementation tree is `8bc36af4e463e515623b05c1fe311ea0e7b73243`.
The raw release archive `evidence-release.tar.gz` has SHA-256
`4b43737e74acaa8af935617294e1e04ff647e49336d555512fd3ae4707decfbb`.
The bundle also stores the original immutable BASS 121/241/481 CSV and
producer receipts, tests, numerical summaries and code. The production
AXBI V4 checkpoints are neither included nor needed for these mini-histories.
