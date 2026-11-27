# Codex execution handoff — HE33

## Immutable inputs and completed work

- repo: cosmosapjw-quantum/BASS_HE
- branch: research/he33-baryon-moment-foundation-20261022
- Draft PR: https://github.com/cosmosapjw-quantum/BASS_HE/pull/86
- unit: research/he33_baryon_moment_foundation_20261022
- immutable science/source/evidence commit: 1d7dab57becc5829f0282b88a7516360ccad718a
- parent HE32 pin: 16a424b7290f484c57e97c8ed74f81e6d2043782
- workflow1.0.0 / approval0.2
- core SHA256: d93e7a88f99a19e1199004bee4730eb0cd1aa250c4da069a72b49aeb07122588
- check source SHA256: fc2d69633f2e9a4573f12c63154fc0e0bc5dab57d0434b4715398b7455f66326

Read README.md, THEORY_KO.md, COMPUTATIONAL_CONTRACT.md, REPORT_KO.md,
DAG.json, NEXT_DAG.json, evidence/VALIDATION.json and delivery/S2_ACK.json.
The later documentation revision contains this handoff and final delivery ACKs;
the scientific code and test source are byte-pinned above.

HE32 remains30/30 complete,394 saved trajectories and six figure pairs.
HE33 is a prescribed-nu_pi, source-free mechanical pressure-moment model;
17 groups ran in current V8 and passed, plus independent Wolfram algebra/oracles.
No HE32 IVP/render/benchmark was repeated. Keep the old results and failure evidence.

## Only new host compatibility gate E0

Current-turn shell calls for Python/C++/Node failed with SERVICE_ERROR before
execution; this is not a finding that the compiler or packages are missing.
Probe the new host live. If Node is available, run the unchanged finite checks
once for the new module-loading/runtime dependency. Use an isolated checkout:

```bash
git fetch origin research/he33-baryon-moment-foundation-20261022
git worktree add --detach ../BASS_HE_HE33 1d7dab57becc5829f0282b88a7516360ccad718a
cd ../BASS_HE_HE33
node --version
node research/he33_baryon_moment_foundation_20261022/checks/check_core.cjs
```

The expected report is groups17,passed17,failed0 and exit0. One process;
no package installation, compiler, NCP sweep or HE32 runner is needed.
The test runner imports only the new mechanical core. Capture stdout/stderr,
exit code, Node version, actual core/test SHA256 and invoked commit. Preserve
failed attempts; inspect an error before any retry. Do not rerun unrelated suites.

## Physics boundary

The pressure tensor uses P=pI+qD with D=diag(-1,-1,2), SI Pa, proper seconds,
nu=pressure-anisotropy decay rate>=0. Inputs H,s,nu are prescribed.
step/advance has Q=j=0. thermalLedger returns the required kinetic power,
including particle creation; it is not a thermal evolution solver.

No calibrated electron/ion/neutral transport matrix, reaction source tensor,
binding/radiation energy coupling or metric feedback is implemented here.
Follow B1/B2/B3 before the new saved-background baryon control B4. Do not
substitute photo/RR frequencies for nu_pi or silently extrapolate CI rates.

The completed HE32 archive remains
BASS_HE_HE32_FINAL_SANDBOX_PILOT_20261021T220535Z.tar.gz,
SHA25627cb0eb0a779815dfaa226849f706df2fed6f0ae6b792383cbc9a0f90635806a,
Dropbox id:BSpOijBcT10AAAAAAD_hsw. Restore saved inputs only when B4 needs them;
never regenerate them by invoking the old campaign.

## Return contract

Return actual commit/hash/runtime, E0 exit/status/stdout summary, any exact failure,
new artifact paths/provider ACKs and unchanged HE32 status. If only E0 succeeds,
report Node compatibility PASS; do not promote to calibrated gas physics.
