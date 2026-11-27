# HE33: baryonic LRS pressure-moment foundation

Workflow **1.0.0**, approval design **0.2**. This separate unit continues from
HE32 publication `16a424b7290f484c57e97c8ed74f81e6d2043782` without altering or replaying its completed
30-stage primordial pilot.

## Scientific question

What pressure-tensor evolution, thermal ledger and positive numerical operator
are required before replacing the HE32 gas closure pi_b=0?

The present completion target is a **mechanical fixed-composition model**:
homogeneous nonrelativistic gas, zero peculiar bulk velocity, no electromagnetic
fields, LRS Bianchi I geometry and a prescribed nonnegative pressure-anisotropy
relaxation rate. It will deliver the derivation, exact constant-coefficient
pressure update, independent controls and an explicit coupling contract.

HE32 matter stress remains the separate collisionless nonbaryonic component.
HE33's gas pressure cannot be relabelled as that existing component. The full
photo/RR network, thermal/source evolution and calibrated multispecies collision
operator are dependencies for a subsequent coupled model.

Read CONTRACT.json, DELTA_INTAKE_KO.md and DAG.json. Source and validation
artifacts are added at their actual completion checkpoints. HE32's 394 saved
trajectories and six figure pairs remain reusable through its verified archive;
no fresh IVP, render or benchmark is required to use them.

## Implemented API and actual validation

The dependency-free source is `src/lrs_baryon_moments.js`. It exports
`invariants, rhs, step, advance, thermalLedger`. Units are SI. The source-free
step solves the frozen 2x2 moment system; advance uses midpoint coefficient
samples. See THEORY_KO.md and COMPUTATIONAL_CONTRACT.md.

The exact core and check source strings were executed in current V8; 17 check
groups passed. The independent Wolfram source/oracles and original failed edge
cases are stored in checks/ and evidence/. The unrun Node module/CLI smoke is a
separate compatibility gate:

```bash
node research/he33_baryon_moment_foundation_20261022/checks/check_core.cjs
```

Expected: `groups=17, passed=17, failed=0`, exit0 on a compatible Node host.
This command performs only the finite mechanical checks and never imports or
runs the HE32 cosmological solver. Current shell service was unavailable, so
Node CLI execution is not claimed. Read REPORT_KO.md and NEXT_DAG.json before
physical coupling. No package installation, compiler or rate service is needed.

## Final delivery

R1–R10 and C1–C10 are complete for this prescribed-rate mechanical model.
Source/evidence pin: `1d7dab57becc5829f0282b88a7516360ccad718a`. Final metadata and two handoffs are in the
later documentation revision. Each stage links its S0/S1/S2/S3 publication and
backup group. Google Drive backups are exact JSON path/content/SHA256 envelopes,
read back before acceptance; Git contains the reviewable files. The old HE32
binary archive is preserved separately and is not duplicated by this unit.
